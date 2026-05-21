# ═══════════════════════════════════════════════════════════════
#  model.py — StegoGAN v9.1 architecture (60-bit)
#
#  Extracted from Cell 4 of StegoGAN_v9_1_60bit_DEMO_COLAB.ipynb
#  The app.py only uses EncoderG and DecoderR for inference.
# ═══════════════════════════════════════════════════════════════

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBNReLU(nn.Module):
    def __init__(self, in_ch, out_ch, kernel=3, stride=1, padding=1):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel, stride, padding, bias=False),
            nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True))
    def forward(self, x): return self.block(x)


class ResBlock(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(ch, ch, 3, 1, 1, bias=False), nn.BatchNorm2d(ch), nn.ReLU(inplace=True),
            nn.Conv2d(ch, ch, 3, 1, 1, bias=False), nn.BatchNorm2d(ch))
    def forward(self, x): return F.relu(x + self.block(x))


class SEBlock(nn.Module):
    """Squeeze-and-Excitation: learns which channels carry message bits."""
    def __init__(self, ch, reduction=16):
        super().__init__()
        self.fc = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(ch, max(ch//reduction, 4)), nn.ReLU(inplace=True),
            nn.Linear(max(ch//reduction, 4), ch), nn.Sigmoid())
    def forward(self, x):
        return x * self.fc(x).unsqueeze(-1).unsqueeze(-1)


class EncoderG(nn.Module):
    """V9.1 U-Net + multi-scale injection + SE attention in bottleneck."""
    def __init__(self, msg_bits=60, ngf=64):
        super().__init__()
        self.msg_fc1 = nn.Linear(msg_bits, ngf)
        self.msg_fc2 = nn.Linear(msg_bits, ngf*2)
        self.msg_fc3 = nn.Linear(msg_bits, ngf*4)
        self.msg_fc4 = nn.Linear(msg_bits, ngf*4)   # 4th scale at 32x32

        self.enc1_conv = ConvBNReLU(3, ngf, 3, 1, 1)
        self.enc1_msg  = ConvBNReLU(ngf*2, ngf, 3, 1, 1)
        self.enc2_down = ConvBNReLU(ngf, ngf*2, 3, 2, 1)
        self.enc2_msg  = ConvBNReLU(ngf*4, ngf*2, 3, 1, 1)
        self.enc3_down = ConvBNReLU(ngf*2, ngf*4, 3, 2, 1)
        self.enc3_msg  = ConvBNReLU(ngf*8, ngf*4, 3, 1, 1)
        self.enc4_down = ConvBNReLU(ngf*4, ngf*4, 3, 2, 1)   # 64→32
        self.enc4_msg  = ConvBNReLU(ngf*8, ngf*4, 3, 1, 1)   # 4th injection

        # Bottleneck with SE attention + 3 ResBlocks
        self.bottleneck = nn.Sequential(
            ConvBNReLU(ngf*4, ngf*4, 3, 2, 1),   # 32→16
            ResBlock(ngf*4), ResBlock(ngf*4), ResBlock(ngf*4),
            SEBlock(ngf*4))

        # Decoder
        self.dec4_up    = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
            ConvBNReLU(ngf*4, ngf*4, 3, 1, 1))
        self.dec4_merge = ConvBNReLU(ngf*8, ngf*4, 3, 1, 1)

        self.dec3_up    = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
            ConvBNReLU(ngf*4, ngf*4, 3, 1, 1))
        self.dec3_merge = ConvBNReLU(ngf*8, ngf*2, 3, 1, 1)

        self.dec2_up    = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
            ConvBNReLU(ngf*2, ngf*2, 3, 1, 1))
        self.dec2_merge = ConvBNReLU(ngf*4, ngf, 3, 1, 1)

        self.dec1_up    = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
            ConvBNReLU(ngf, ngf, 3, 1, 1))
        self.dec1_merge = ConvBNReLU(ngf*2, ngf//2, 3, 1, 1)
        self.out_conv   = nn.Conv2d(ngf//2, 3, 3, 1, 1)

    def forward(self, image, msg, delta_scale=0.1):
        B, C, H, W = image.shape
        m1 = self.msg_fc1(msg).unsqueeze(-1).unsqueeze(-1).expand(-1,-1,H,W)
        m2 = self.msg_fc2(msg).unsqueeze(-1).unsqueeze(-1).expand(-1,-1,H//2,W//2)
        m3 = self.msg_fc3(msg).unsqueeze(-1).unsqueeze(-1).expand(-1,-1,H//4,W//4)
        m4 = self.msg_fc4(msg).unsqueeze(-1).unsqueeze(-1).expand(-1,-1,H//8,W//8)

        e1 = self.enc1_msg(torch.cat([self.enc1_conv(image), m1], dim=1))
        e2 = self.enc2_msg(torch.cat([self.enc2_down(e1), m2], dim=1))
        e3 = self.enc3_msg(torch.cat([self.enc3_down(e2), m3], dim=1))
        e4 = self.enc4_msg(torch.cat([self.enc4_down(e3), m4], dim=1))
        e5 = self.bottleneck(e4)

        d4 = self.dec4_merge(torch.cat([self.dec4_up(e5), e4], dim=1))
        d3 = self.dec3_merge(torch.cat([self.dec3_up(d4), e3], dim=1))
        d2 = self.dec2_merge(torch.cat([self.dec2_up(d3), e2], dim=1))
        d1 = self.dec1_merge(torch.cat([self.dec1_up(d2), e1], dim=1))
        return torch.clamp(image + delta_scale * torch.tanh(self.out_conv(d1)), -1, 1)


class DecoderR(nn.Module):
    """V9.1 R: conv+ResBlocks + SE attention + deep MLP head.
    Always float32 (BN overflow in fp16).
    """
    def __init__(self, msg_bits=60, nrf=64):
        super().__init__()
        self.features = nn.Sequential(
            ConvBNReLU(3, nrf, 3, 2, 1),                # 256→128
            ConvBNReLU(nrf, nrf*2, 3, 2, 1),            # 128→64
            ResBlock(nrf*2),
            ConvBNReLU(nrf*2, nrf*4, 3, 2, 1),          # 64→32
            ResBlock(nrf*4),
            ConvBNReLU(nrf*4, nrf*8, 3, 2, 1),          # 32→16
            ResBlock(nrf*8),
            ConvBNReLU(nrf*8, nrf*8, 3, 2, 1),          # 16→8
            SEBlock(nrf*8),                               # channel attention
            ConvBNReLU(nrf*8, nrf*8, 3, 2, 1),          # 8→4
            nn.AdaptiveAvgPool2d(1))
        # Deeper MLP: 3 FC layers
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(nrf*8, 512), nn.ReLU(inplace=True), nn.Dropout(0.3),
            nn.Linear(512, 256),   nn.ReLU(inplace=True), nn.Dropout(0.2),
            nn.Linear(256, msg_bits))

    def forward(self, x):
        return self.classifier(self.features(x.float()))  # always float32


class PatchDiscriminator(nn.Module):
    def __init__(self, ndf=64):
        super().__init__()
        self.model = nn.Sequential(
            nn.utils.spectral_norm(nn.Conv2d(6, ndf, 4, 2, 1)),     nn.LeakyReLU(0.2, inplace=True),
            nn.utils.spectral_norm(nn.Conv2d(ndf, ndf*2, 4, 2, 1)), nn.LeakyReLU(0.2, inplace=True),
            nn.utils.spectral_norm(nn.Conv2d(ndf*2, ndf*4, 4, 2, 1)), nn.LeakyReLU(0.2, inplace=True),
            nn.utils.spectral_norm(nn.Conv2d(ndf*4, ndf*4, 4, 1, 1)), nn.LeakyReLU(0.2, inplace=True),
            nn.utils.spectral_norm(nn.Conv2d(ndf*4, 1, 4, 1, 1)))
    def forward(self, ref, query):
        return self.model(torch.cat([ref, query], dim=1))


class NoiseLayer(nn.Module):
    """Gaussian noise + pixel dropout, both ramped."""
    def __init__(self): super().__init__()
    def forward(self, x, epoch, config=None):
        if not self.training: return x
        std = config.get_noise_std(epoch) if config else 0.02
        dp  = config.get_dropout_p(epoch) if config else 0.02
        if std > 0: x = x + torch.randn_like(x) * std
        if dp > 0:  x = x * (torch.rand_like(x) > dp).float()
        return torch.clamp(x, -1, 1)
