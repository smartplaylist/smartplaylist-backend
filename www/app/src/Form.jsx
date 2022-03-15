import React from "react";

class Form extends React.Component {
    render() {
        return (
            <form className="pure-form" id="form">
                <fieldset>
                    <legend>Search for tracks</legend>
                    <label htmlFor="input">Artist or title</label>
                    <input
                        type="text"
                        id="query"
                        name="query"
                        label="Search track"
                        onChange={this.props.handler}
                        value={this.props.values.query}
                    />
                    <label htmlFor="releaseDate">Released</label>
                    <input
                        type="date"
                        id="releaseDate"
                        name="releaseDate"
                        onChange={(e) => this.props.handler(e)}
                        label="releaseDate"
                        value={this.props.values.releaseDate}
                    />
                    <label htmlFor="minTempo">Min. BPM</label>
                    <input
                        type="number"
                        id="minTempo"
                        name="minTempo"
                        onChange={(e) => this.props.handler(e)}
                        label="Min. BPM s"
                        value={this.props.values.minTempo}
                    />
                    <label htmlFor="maxTempo">Max. BPM</label>
                    <input
                        type="number"
                        id="maxTempo"
                        name="maxTempo"
                        onChange={(e) => this.props.handler(e)}
                        label="Max. BPM s"
                        value={this.props.values.maxTempo}
                    />
                    <label htmlFor="genres">Genres</label>
                    <input
                        type="text"
                        id="genres"
                        name="genres"
                        onChange={(e) => this.props.handler(e)}
                        label="Genres"
                        value={this.props.values.genres}
                    />
                    <label htmlFor="explicit">
                        <input
                            type="checkbox"
                            id="explicit"
                            name="explicit"
                            onChange={(e) => this.props.handler(e)}
                            label="Explicit"
                            value={this.props.values.explicit}
                        />
                        Explicit
                    </label>
                    <label htmlFor="key">Key</label>
                    <select
                        id="key"
                        name="key"
                        onChange={(e) => this.props.handler(e)}
                        label="Key"
                        value={this.props.values.key}
                    >
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
                    <button
                        type="submit"
                        name="submit"
                        className="pure-button pure-button-primary"
                    >
                        Search
                    </button>
                </fieldset>
            </form>
        );
    }
}

export default Form;
