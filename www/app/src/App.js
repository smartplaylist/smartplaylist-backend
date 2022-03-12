import "./App.css";
import React, { useEffect, useState } from "react";

function App() {
    const [tracks, setTracks] = useState([]);

    const fetchData = (query) => {
        fetch(
            `http://127.0.0.1:3000/tracks?select=all_artists,name,genres,release_date,tempo,key,preview_url?limit=100&tempo=lt.140&tempo=gt.120&or=(name.ilike.*${query}*,main_artist.ilike.*${query}*)`
        )
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                setTracks(data);
            });
    };

    const handleOnChange = (e, param) => {
        const query = e.target.value;
        fetchData(query, param);
    };

    useEffect(() => {
        fetchData("");
        document.getElementById("input").focus();
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Spotify Grabtrack (aka. Smart Spotify playlist)</h1>
            </header>
            <div id="main">
                <form className="pure-form" id="form">
                    <fieldset>
                        <legend>Search for tracks</legend>
                        <label htmlFor="input">Artist or title</label>
                        <input
                            type="text"
                            id="input"
                            onChange={(e) => handleOnChange(e, "text")}
                            label="Search track"
                        />
                        <label htmlFor="min-bpm">Min. BPM</label>
                        <input
                            type="number"
                            id="min-bpm"
                            onChange={handleOnChange}
                            label="Min. BPM s"
                        />
                        <label htmlFor="default-remember">
                            <input type="checkbox" id="default-remember" />{" "}
                            Explicit
                        </label>
                        <button
                            type="submit"
                            className="pure-button pure-button-primary"
                        >
                            Search
                        </button>
                    </fieldset>
                </form>
                <div id="tracks">
                    <h2>Tracks</h2>

                    {tracks.length > 0 && (
                        <table className="pure-table pure-table-bordered pure-table-striped">
                            <thead>
                                <tr>
                                    <th>Play</th>
                                    {/* <th>Main artist</th> */}
                                    <th>Artists</th>
                                    <th>Title</th>
                                    <th>Genres</th>
                                    <th>Release date</th>
                                    <th>Tempo</th>
                                    <th>Key</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tracks.map((track) => (
                                    <tr key={track.id}>
                                        <td>
                                            <a href={track.preview_url}>PLAY</a>
                                        </td>
                                        {/* <td>{track.main_artist}</td> */}
                                        <td>
                                            {track.all_artists.map(
                                                (artist, i) => (
                                                    <span>
                                                        {i > 0 && ", "}
                                                        {artist}
                                                    </span>
                                                )
                                            )}
                                        </td>
                                        <td>{track.name}</td>
                                        <td>
                                            {track.genres.map((genre, i) => (
                                                <span key={i}>
                                                    {i > 0 && ", "}
                                                    {genre}
                                                </span>
                                            ))}
                                        </td>

                                        <td>{track.release_date}</td>
                                        <td>{track.tempo}</td>
                                        <td>{track.key}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
