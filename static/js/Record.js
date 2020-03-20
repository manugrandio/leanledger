import React, { Component } from "react";


const DEBIT = "debit";
const CREDIT = "credit";


class Record extends Component {
  constructor(props) {
    super(props);
    this.accounts = [
      {id: 1, type: "D", name: "cash", url: ""},
      {id: 2, type: "O", name: "expense one", url: ""},
      {id: 3, type: "O", name: "expense two", url: ""},
      {id: 4, type: "D", name: "lent", url: ""},
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

  addVariation(e, variationType) {
    e.preventDefault();
    let record = this.state.record, variations = record.variations[variationType];
    let newId = Math.max(...variations.map((variation) => variation.id)) + 1;
    record.variations[variationType].push({
      id: newId,
      amount: "",
      account_id: this.accounts[0].id,
      account_name: this.accounts[0].name,
      account_url: this.accounts[0].url,
    });
    this.setState({ record: record });
  }

  deleteVariation(variationType, variationID) {
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
            addVariation={ (e, variationType) => this.addVariation(e, variationType) }
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
              className="form-control form-control-sm"
              value={ this.props.date }
              onChange={ (e) => this.props.onChange("date", e) }
            />
          </div>
          <div className="col">
            <input
              type="text"
              placeholder="Description"
              className="form-control form-control-sm"
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

    let finishUpdateBtn = null, addDebitVariationBtn = null, addCreditVariationBtn = null;
    if (this.props.editMode) {
      finishUpdateBtn = (
        <button
          className="btn btn-primary mt-3"
          onClick={ () => this.props.finishUpdate() }
        >
          Done
        </button>
      );
      addDebitVariationBtn = (
        <>
          <tr>
            <td></td>
            <td>
              <a href="" onClick={ (e) => this.props.addVariation(e, DEBIT) }><small>Add</small></a>
            </td>
          </tr>
        </>
      );
      addCreditVariationBtn = (
        <>
          <tr>
            <td></td>
            <td>
              <a href="" onClick={ (e) => this.props.addVariation(e, CREDIT) }><small>Add</small></a>
            </td>
          </tr>
        </>
      );
    }

    return (
      <div className="card-body">
        <table className="table table-borderless table-sm mb-0">
          <tbody>
            { debitVariations }
            { addDebitVariationBtn }
            { creditVariations }
            { addCreditVariationBtn }
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

    let accountColumn,
      accountColumnClass = this.props.variationType === CREDIT ? "ml-5" : "",
      deleteColumn = null;
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
      const accountColumnOptions = this.props.accounts.map((account) => (
        <option key={ account.id } value={ account.id }>{ account.type }: { account.name }</option>
      ));
      accountColumn = (
        <select style={{ width: "70%" }} className={ "form-control form-control-sm " + accountColumnClass } onChange={ () => null }>
          { accountColumnOptions }
        </select>
      );
    } else {
      accountColumn = (
        <span className={ accountColumnClass }>
          <a href={ this.props.account_url }>{ this.props.account_name }</a>
        </span>
      );
    }
    return (
      <tr>
        { deleteColumn }
        <td scope="row">
          { accountColumn }
        </td>
        { this.props.variationType === DEBIT ? valueColumn : emptyColumn }
        { this.props.variationType === DEBIT ? emptyColumn : valueColumn }
      </tr>
    );
  }
}


export default Record;
