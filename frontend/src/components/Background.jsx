import './Background.css';

export default function Background() {
  return (
    <div className="bg-container" aria-hidden="true">
      <div className="bg-orb bg-orb--cyan" />
      <div className="bg-orb bg-orb--violet" />
      <div className="bg-orb bg-orb--emerald" />
      <div className="bg-grid" />
      <div className="bg-noise" />
    </div>
  );
}
