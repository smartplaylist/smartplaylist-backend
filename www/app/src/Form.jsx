import React from "react";
import MinMaxFilter from "./MinMaxFilter";

export default class Form extends React.Component {
    constructor(props) {
        super(props);

        this.minMaxFilters = [
            {
                name: "MainArtistPopularity",
                label: "Main artist popularity",
                minValue: this.props.values.minMainArtistPopularity,
                maxValue: this.props.values.maxMainArtistPopularity,
            },
            {
                name: "Tempo",
                label: "Tempo (BPM)",
                minValue: this.props.values.minTempo,
                maxValue: this.props.values.maxTempo,
            },
            {
                name: "Popularity",
                label: "Track popularity",
                minValue: this.props.values.minPopularity,
                maxValue: this.props.values.maxPopularity,
            },
        ];
    }

    render() {
        return (
            <form className="pure-form" id="form" autoComplete="off">
                <fieldset>
                    <div className="filter">
                        <legend>Search for tracks</legend>
                        <label htmlFor="input">Artist or title</label>
                        <input
                            type="text"
                            id="query"
                            name="query"
                            onChange={this.props.handler}
                            value={this.props.values.query}
                        />
                        <label htmlFor="genres">Genres</label>
                        <input
                            type="text"
                            id="genres"
                            name="genres"
                            onChange={this.props.handler}
                            value={this.props.values.genres}
                        />
                        <label htmlFor="releaseDate">Released</label>
                        <input
                            type="date"
                            id="releaseDate"
                            name="releaseDate"
                            onChange={this.props.handler}
                            value={this.props.values.releaseDate}
                        />
                    </div>

                    {this.minMaxFilters.map((filter, i) => (
                        <MinMaxFilter
                            label={filter.label}
                            name={filter.name}
                            minValue={filter.minValue}
                            maxValue={filter.maxValue}
                            key={filter.name + "-" + i}
                            handler={this.props.handler}
                        />
                    ))}
                    <label htmlFor="key">Key</label>
                    <select
                        id="key"
                        name="key"
                        onChange={this.props.handler}
                        label="Key"
                        value={this.props.values.key}
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
                        onChange={this.props.handler}
                        value={this.props.values.explicit}
                    />
                </fieldset>
            </form>
        );
    }
}
