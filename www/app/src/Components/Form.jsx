import React from "react";
import MinMaxFilter from "./MinMaxFilter";
import "./Form.css";

function Form(props) {
    const minMaxFilters = [
        {
            name: "Tempo",
            label: "Tempo (bpm)",
            minValue: props.values.minTempo,
            maxValue: props.values.maxTempo,
            showColumn: props.values.showColumnTempo,
        },
        {
            name: "Popularity",
            label: "Track popularity",
            minValue: props.values.minPopularity,
            maxValue: props.values.maxPopularity,
            showColumn: props.values.showColumnPopularity,
        },
        {
            name: "MainArtistPopularity",
            label: "Main artist popularity",
            minValue: props.values.minMainArtistPopularity,
            maxValue: props.values.maxMainArtistPopularity,
            showColumn: props.values.showColumnMainArtistPopularity,
        },
        {
            name: "MainArtistFollowers",
            label: "Main artist followers",
            minValue: props.values.minMainArtistFollowers,
            maxValue: props.values.maxMainArtistFollowers,
            showColumn: props.values.showColumnMainArtistFollowers,
        },
        {
            name: "Danceability",
            label: "Danceability",
            minValue: props.values.minDanceability,
            maxValue: props.values.maxDanceability,
            showColumn: props.values.showColumnDanceability,
        },
        {
            name: "Energy",
            label: "Energy",
            minValue: props.values.minEnergy,
            maxValue: props.values.maxEnergy,
            showColumn: props.values.showColumnEnergy,
        },
        {
            name: "Speechiness",
            label: "Speechiness",
            minValue: props.values.minSpeechiness,
            maxValue: props.values.maxSpeechiness,
            showColumn: props.values.showColumnSpeechiness,
        },
        {
            name: "Acousticness",
            label: "Acousticness",
            minValue: props.values.minAcousticness,
            maxValue: props.values.maxAcousticness,
            showColumn: props.values.showColumnAcousticness,
        },
        {
            name: "Instrumentalness",
            label: "Instrumentalness",
            minValue: props.values.minInstrumentalness,
            maxValue: props.values.maxInstrumentalness,
            showColumn: props.values.showColumnInstrumentalness,
        },
        {
            name: "Liveness",
            label: "Liveness",
            minValue: props.values.minLiveness,
            maxValue: props.values.maxLiveness,
            showColumn: props.values.showColumnLiveness,
        },
        {
            name: "Valence",
            label: "Valence",
            minValue: props.values.minValence,
            maxValue: props.values.maxValence,
            showColumn: props.values.showColumnValence,
        },
    ];

    return (
        <form className="pure-form" id="form" autoComplete="off">
            <fieldset>
                <div className="filter">
                    <label htmlFor="input">Artist or title</label>
                    <input
                        type="text"
                        id="query"
                        name="query"
                        onChange={props.handler}
                        value={props.values.query}
                    />
                    <label htmlFor="genres">Genres</label>
                    <input
                        type="text"
                        id="genres"
                        name="genres"
                        onChange={props.handler}
                        value={props.values.genres}
                    />
                    <label htmlFor="releaseDate">Released after</label>
                    <input
                        type="date"
                        id="releaseDate"
                        name="releaseDate"
                        onChange={props.handler}
                        value={props.values.releaseDate}
                    />
                </div>

                <div className="filter">
                    <label htmlFor="key">Key</label>
                    <select
                        id="key"
                        name="key"
                        onChange={props.handler}
                        label="Key"
                        value={props.values.key}
                    >
                        <option value="any">Any</option>
                        <option value="0">C</option>
                        <option value="1">C♯</option>
                        <option value="2">D</option>
                        <option value="3">D♯</option>
                        <option value="4">E</option>
                        <option value="5">F</option>
                        <option value="6">F♯</option>
                        <option value="7">G</option>
                        <option value="8">G♯</option>
                        <option value="9">A</option>
                        <option value="10">A♯</option>
                        <option value="11">B</option>
                    </select>
                    <label htmlFor="explicit">Explicit</label>
                    <input
                        type="checkbox"
                        id="explicit"
                        name="explicit"
                        onChange={props.handler}
                        value={props.values.explicit}
                        defaultChecked={props.values.explicit}
                    />
                    <label htmlFor="followed">Only followed artists</label>
                    <input
                        type="checkbox"
                        id="followed"
                        name="followed"
                        onChange={props.handler}
                        value={props.values.followed}
                        defaultChecked={props.values.followed}
                    />
                </div>

                {minMaxFilters.map((filter, i) => (
                    <MinMaxFilter
                        label={filter.label}
                        name={filter.name}
                        minValue={filter.minValue}
                        maxValue={filter.maxValue}
                        showColumn={filter.showColumn}
                        key={filter.name + "-" + i}
                        handler={props.handler}
                    />
                ))}
            </fieldset>
        </form>
    );
}

export default Form;
