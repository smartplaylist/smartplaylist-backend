import "./App.css";
import React, { useEffect, useState, useMemo } from "react";
import Form from "./Form";
import Player from "./Player";
import Stats from "./Stats";
import TrackList from "./TrackList";

const HOST = `http://127.0.0.1:3000`;
const FETCH_DELAY = 500;

function App() {
    const [totalResults, setTotalResults] = useState(0);
    const [totalTracks, setTotalTracks] = useState(0);
    const [previewUrl, setPreviewUrl] = useState("");
    const [tracks, setTracks] = useState([]);
    const [form, setForm] = useState({
        query: "",
        genres: "",
        releaseDate: "2020-01-01",

        minTempo: 80,
        maxTempo: 210,
        showColumnTempo: "true",

        minPopularity: 0,
        maxPopularity: 100,
        showColumnPopularity: "true",

        minMainArtistPopularity: 1,
        maxMainArtistPopularity: 100,
        showColumnMainArtistPopularity: "true",

        minMainArtistFollowers: 1,
        maxMainArtistFollowers: 50000000,
        showColumnMainArtistFollowers: "true",

        minDanceability: 0,
        maxDanceability: 1000,
        showColumnDanceability: "true",

        minEnergy: 0,
        maxEnergy: 1000,
        showColumnEnergy: "true",

        minSpeechiness: 0,
        maxSpeechiness: 1000,
        showColumnSpeechiness: "true",

        minAcousticness: 0,
        maxAcousticness: 1000,
        showColumnAcousticness: "true",

        minInstrumentalness: 0,
        maxInstrumentalness: 1000,
        showColumnInstrumentalness: "true",

        minLiveness: 0,
        maxLiveness: 1000,
        showColumnLiveness: "true",

        minValence: 0,
        maxValence: 1000,
        showColumnValence: "true",

        explicit: "checked",
        key: "any",
    });

    const fetchTotalTracks = () => {
        let url = HOST;

        url += `/tracks?select=spotify_id`;
        url += `&limit=1`;
        url += `&energy=not.is.null`;

        fetch(url, {
            headers: { Prefer: "count=estimated" },
        }).then((response) => {
            let count = response.headers.get("Content-Range");
            setTotalTracks(count.split("/")[1]);
        });
    };

    const fetchData = (form) => {
        const LIMIT = 100;

        let url = HOST;
        url += `/tracks`;
        url += `?select=spotify_id,all_artists,name,genres,release_date,tempo,popularity,danceability,energy,speechiness,acousticness,instrumentalness,liveness,valence,main_artist_popularity,main_artist_followers,key,preview_url`;
        url += `&order=release_date.desc,popularity.desc,spotify_id.asc`;
        url += `&limit=${LIMIT}`;
        url += `&tempo=gte.${form.minTempo}&tempo=lte.${form.maxTempo}`;
        url += `&popularity=gte.${form.minPopularity}&popularity=lte.${form.maxPopularity}`;
        url += `&main_artist_popularity=gte.${form.minMainArtistPopularity}&main_artist_popularity=lte.${form.maxMainArtistPopularity}`;
        url += `&main_artist_followers=gte.${form.minMainArtistFollowers}&main_artist_followers=lte.${form.maxMainArtistFollowers}`;
        url += `&danceability=gte.${form.minDanceability}&danceability=lte.${form.maxDanceability}`;
        url += `&energy=gte.${form.minEnergy}&energy=lte.${form.maxEnergy}`;
        url += `&speechiness=gte.${form.minSpeechiness}&speechiness=lte.${form.maxSpeechiness}`;
        url += `&acousticness=gte.${form.minAcousticness}&acousticness=lte.${form.maxAcousticness}`;
        url += `&instrumentalness=gte.${form.minInstrumentalness}&instrumentalness=lte.${form.maxInstrumentalness}`;
        url += `&liveness=gte.${form.minLiveness}&liveness=lte.${form.maxLiveness}`;
        url += `&valence=gte.${form.minValence}&valence=lte.${form.maxValence}`;

        const searchQuery = form.query.trim().replace(/\s\s+/g, " ").split(" ");
        searchQuery.forEach((element) => {
            url += `&or=(name.ilike.*${element}*,all_artists_string.ilike.*${element}*)`;
        });

        const genresQuery = form.genres
            .trim()
            .replace(/\s\s+/g, " ")
            .split(" ");
        // Use `or` or `and` depending on the logic you need (genre has any or all of the strings)
        url += `&or=(`;
        genresQuery.forEach((element) => {
            url += `genres_string.ilike.*${element}*,`;
        });
        url = url.slice(0, -1);
        url += `)`;
        url += `&release_date=gte.${form.releaseDate}`;
        if (form.key !== "any") url += `&key=eq.${form.key}`;

        fetch(url, {
            headers: { Prefer: "count=exact" },
        })
            .then((response) => {
                let count = response.headers.get("Content-Range");
                setTotalResults(count.split("/")[1]);
                return response.json();
            })
            .then((data) => {
                setTracks(data);
            });
    };

    // Debouncing with arguments
    // https://dev.to/monaye/refactor-davidwalsh-s-debounce-function-5afc
    const debounce = (func, delay, immediate) => {
        let timerId;
        return (...args) => {
            const boundFunc = func.bind(this, ...args);
            clearTimeout(timerId);
            if (immediate && !timerId) {
                boundFunc();
            }
            const calleeFunc = immediate
                ? () => {
                      timerId = null;
                  }
                : boundFunc;
            timerId = setTimeout(calleeFunc, delay);
        };
    };

    const debouncedFetchData = useMemo(
        () => debounce(fetchData, FETCH_DELAY),
        []
    );

    // Run on first render, ex componentDidMount()
    // Second parameter is `[]` to run only when an empty table changes (which results in only one run)
    useEffect(() => {
        document.getElementById("query").focus();
        // TODO: Create "initialLoad" view in database to grab all needed initial data
        // Like: total tracks, max artist followers?
        fetchTotalTracks();
    }, []);

    // ex componentDidUpdate()
    useEffect(() => {
        debouncedFetchData(form);
    }, [debouncedFetchData, form]);

    // Update state based on form's elements and their name
    const handleFormChange = (e) => {
        setForm((prev) => ({
            ...prev,
            [e.target.name]: e.target.value,
        }));
    };

    const setPlayerSong = (url) => {
        setPreviewUrl(url);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Spotify smart playlist generator</h1>
            </header>
            <div id="main">
                <Stats totalResults={totalResults} totalTracks={totalTracks} />
                <Form handler={handleFormChange} values={form} />

                <TrackList
                    tracks={tracks}
                    values={form}
                    onPlayClick={setPlayerSong}
                />
                <Player previewUrl={previewUrl} />
            </div>
        </div>
    );
}

export default App;
