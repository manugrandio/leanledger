import React, { Component } from "react";


const DEBIT = "debit";
const CREDIT = "credit";


class Record extends Component {
  constructor(props) {
    super(props);
    this.accounts = [
      {value: 1, type: "D", name: "cash"},
      {value: 2, type: "O", name: "expense one"},
      {value: 3, type: "O", name: "expense two"},
      {value: 4, type: "D", name: "lent"},
    ];
    this.state = {record: null, editMode: false};
    this.getRecord();
  }

  getRecord() {
    const self = this;
    const recordUrl = this.getRecordUrl();
    return fetch(recordUrl)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        self.setState({record: data});
      });
  }

  getRecordUrl() {
    // TODO clean
    const currentUrl = new URL(window.location.href);
    const pathUrlParts = currentUrl.pathname.split("/");
    const ledgerId = pathUrlParts[2];
    const recordId = pathUrlParts[pathUrlParts.length - 2];
    const urlPath = `/ledger/${ledgerId}/record/${recordId}.json`;
    return currentUrl.origin + urlPath;
  }

  enterEditMode(e) {
    e.preventDefault();
    this.setState({ editMode: true });
  }

  finishUpdate() {
    // TODO update record to back-end
    this.setState({ editMode: false });
  }

  onChange(field, e) {
    let record = this.state.record;
    record[field] = e.target.value;
    this.setState({ record: record });
  }

  deleteVariation(variationType, variationID) {
    console.log(variationType);
    let record = this.state.record, variations = record.variations[variationType];
    record.variations[variationType] = variations.filter((variation) => variation.id !== variationID);
    this.setState({ record: record });
  }

  render() {
    if (this.state.record === null) {
      return <p className="mt-3">Loading…</p>;
    } else {
      const cardContent = (
        <>
          <RecordHeader
            {...this.state.record}
            onChange={ (field, e) => this.onChange(field, e) }
            editMode={ this.state.editMode }
            enterEditMode={ (e) => this.enterEditMode(e) }
          />
          <RecordBody
            {...this.state.record}
            accounts={ this.accounts }
            deleteVariation={ (variationType, variationID) => this.deleteVariation(variationType, variationID) }
            editMode={ this.state.editMode }
            finishUpdate={ () => this.finishUpdate() }
          />
        </>
      );
      let card;
      if (this.state.editMode) {
        card = <form>{ cardContent }</form>;
      } else {
        card = cardContent;
      }
      return (
        <div className="card mt-3 shadow-sm">{ card }</div>
      );
    }
  }
}


class RecordHeader extends Component {
  render() {
    let headerContent;
    if (this.props.editMode) {
      headerContent = (
        <div className="form-row">
          <div className="col">
            <input
              type="text"
              placeholder="Date"
              className="form-control"
              value={ this.props.date }
              onChange={ (e) => this.props.onChange("date", e) }
            />
          </div>
          <div className="col">
            <input
              type="text"
              placeholder="Description"
              className="form-control"
              value={ this.props.description }
              onChange={ (e) => this.props.onChange("description", e) }
            />
          </div>
        </div>
      )
    } else {
      let balancedState;
      if (this.props.is_balanced) {
        balancedState = <span className="float-right badge badge-success align-bottom">ok</span>;
      } else {
        balancedState = <span className="float-right badge badge-danger">unbalanced</span>;
      }
      headerContent = (
        <>
          <strong>{ this.props.date }</strong>
          <em className="ml-2">{ this.props.description }</em>
          <a href="" className="ml-2" onClick={ (e) => this.props.enterEditMode(e) }>
            <small>Edit</small>
          </a>
          { balancedState }
        </>
      );
    }

    return (
      <div className="card-header">
        { headerContent }
      </div>
    );
  }
}


class RecordBody extends Component {
  render() {
    const debitVariations = this.props.variations.debit.map((variation) => (
      <Variation
        key={ variation.id }
        variationType={ DEBIT }
        deleteVariation={ (variationType, variationID) => this.props.deleteVariation(variationType, variationID) }
        editMode={ this.props.editMode }
        accounts={ this.props.accounts }
        {...variation}
      />
    ));
    const creditVariations = this.props.variations.credit.map((variation) => (
      <Variation
        key={ variation.id }
        variationType={ CREDIT }
        deleteVariation={ (variationType, variationID) => this.props.deleteVariation(variationType, variationID) }
        editMode={ this.props.editMode }
        accounts={ this.props.accounts }
        {...variation}
      />
    ));

    let finishUpdateBtn = null;
    if (this.props.editMode) {
      finishUpdateBtn = (
        <button
          className="btn btn-primary mt-3"
          onClick={ () => this.props.finishUpdate() }
        >
          Done
        </button>
      );
    }

    return (
      <div className="card-body">
        <table className="table table-borderless table-sm mb-0">
          <tbody>
            { debitVariations }
            { creditVariations }
          </tbody>
        </table>
        { finishUpdateBtn }
      </div>
    );
  }
}


class Variation extends Component {
  render() {
    const emptyColumn = <td></td>;
    const valueColumn = (
      <td>
        <span className="float-right">{ this.props.amount }</span>
      </td>
    );

    let deleteColumn = null;
    if (this.props.editMode) {
      deleteColumn = (
        <td style={{ width: "1em" }}>
          <span
            className="text-danger"
            style={{ cursor: "pointer" }}
            onClick={ () => this.props.deleteVariation(this.props.variationType, this.props.id) }
          >
            ✗
          </span>
        </td>
      );
    }
    return (
      <tr>
        { deleteColumn }
        <td scope="row">
          <span className={ this.props.variationType === CREDIT ? 'ml-5' : '' }>
            <a href={ this.props.account_url }>{ this.props.account_name }</a>
          </span>
        </td>
        { this.props.variationType === DEBIT ? valueColumn : emptyColumn }
        { this.props.variationType === DEBIT ? emptyColumn : valueColumn }
      </tr>
    );
  }
}


export default Record;
