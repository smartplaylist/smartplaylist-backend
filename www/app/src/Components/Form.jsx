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
                />
            </fieldset>
        </form>
    );
}

export default Form;
