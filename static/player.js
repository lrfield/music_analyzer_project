// Based on tutorial: https://www.codewithfaraz.com/content/459/create-a-music-search-app-using-html-css-and-javascript
async function fetchMusic(artistName) {
    const url = `https://itunes.apple.com/search?media=music&limit=1&attribute=artistTerm&term=${encodeURIComponent(artistName)}`;
    const response = await fetch(url);
    const data = await response.json();
    const song = data.results[0];

    const div = document.createElement('div');
    div.innerHTML = `
    <div class="box" style="display:flex; flex-direction:row; gap:12px;">
        <img src="${song.artworkUrl100}" style = "filter:invert(1);"/>
        <div style="display:flex; flex-direction:column;">
        <p>${song.trackName}</p>
        <p>${song.artistName}</p>
        <audio class="audio-preview" controls>
        <source src="${song.previewUrl}" type="audio/mpeg">
        </audio>
        </div>
    </div>
    `;
    return div;
}