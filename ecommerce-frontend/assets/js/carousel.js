function initArrowCarousel(trackId, prevId, nextId, step = 360) {
  const track = document.getElementById(trackId);
  const prev = document.getElementById(prevId);
  const next = document.getElementById(nextId);
  if (!track || !prev || !next) return;
  prev.addEventListener('click', () => track.scrollBy({ left: -step, behavior: 'smooth' }));
  next.addEventListener('click', () => track.scrollBy({ left: step, behavior: 'smooth' }));
}
