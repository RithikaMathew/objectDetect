import { useEffect, useLayoutEffect, useState } from "react";
import Home from "./Home";
import Job from "./Job";
import StudyGuide from "./StudyGuide";



export default function App() {
  const [hash, setHash] = useState(() => location.hash);
  const id = hash.startsWith("#/job/") ? hash.slice(6) : null;
  const section = hash === "#analyze" ? "analyze" : hash === "#library" ? "library" : "overview";
  const scrollToSection = () => {
    if (id) return;
    if (section === "overview") window.scrollTo(0, 0);
    else document.getElementById(section)?.scrollIntoView({block: "start"});
  };
  useLayoutEffect(scrollToSection, [hash]);
  useEffect(() => {
    const h = () => setHash(location.hash);
    addEventListener("hashchange", h);
    return () => removeEventListener("hashchange", h);
  }, []);
  return (
    <div className="app">
      <header className="top">
        <a href="#/" className="brand"><span className="brand-mark" aria-hidden="true">◎</span>CycleScope</a>
        <span className="tag">Traffic safety research</span><nav className="header-nav" aria-label="Main navigation" onClick={e => { if (e.target.closest("a")?.getAttribute("href") === location.hash) scrollToSection(); }}><a href="#/" aria-current={!id && section === "overview" ? "location" : undefined}>Overview</a><a href="#analyze" aria-current={!id && section === "analyze" ? "location" : undefined}>Analyze</a><a href="#library" aria-current={!id && section === "library" ? "location" : undefined}>Video library</a></nav><span className="local-badge">Local workspace</span>
      </header>
      <main>{id ? <Job key={id} id={id} /> : <Home />}</main>
      <StudyGuide jobId={id}/>
    </div>
  );
}
