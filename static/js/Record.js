import React, { Component } from "react";


const DEBIT = "debit";
const CREDIT = "credit";


class Record extends Component {
  constructor(props) {
    super(props);
    this.state = {record: null, editMode: false, accounts: null};
    this.getRecord();
  }

  getRecord() {
    const self = this;
    const recordUrl = this.getRecordUrl();
    fetch(recordUrl)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        self.setState({record: data});
      });
  }

  getRecordUrl() {
    const { origin, ledgerId, recordId } = this.getUrlParts();
    const urlPath = `/ledger/${ledgerId}/record/${recordId}.json`;
    return origin + urlPath;
  }

  getUrlParts() {
    // TODO clean
    const currentUrl = new URL(window.location.href);
    const pathUrlParts = currentUrl.pathname.split("/");
    return {
      ledgerId: pathUrlParts[2],
      recordId: pathUrlParts[pathUrlParts.length - 2],
      origin: currentUrl.origin,
    };
  }

  enterEditMode(e) {
    e.preventDefault();
    const { origin, ledgerId } = this.getUrlParts();
    const urlPath = `/ledger/${ledgerId}/account.json`;
    const accountsUrl = origin + urlPath;
    fetch(accountsUrl)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        this.setState({ editMode: true, accounts: data });
      });
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
      account_id: this.state.accounts[0].id,
      account_name: this.state.accounts[0].name,
      account_url: this.state.accounts[0].url,
    });
    this.setState({ record: record });
  }

  deleteVariation(variationType, variationID) {
    let record = this.state.record, variations = record.variations[variationType];
    record.variations[variationType] = variations.filter((variation) => variation.id !== variationID);
    this.setState({ record: record });
  }

  changeVariationAccount(e, variationType, variationId) {
    // TODO change variations to be an object instead of a dict
    const accountId = parseInt(e.target.value);
    let record = this.state.record,
      variations = record.variations[variationType],
      originalVariation = variations.filter((variation) => variation.id === variationId)[0],
      account = this.state.accounts.filter((account) => account.id === accountId)[0];
    originalVariation.account_id = account.id;
    originalVariation.account_name = account.name;
    originalVariation.account_url = account.url;
    this.setState({ record: record });
  }

  changeVariationAmount(e, variationType, variationId) {
    let record = this.state.record,
      variations = record.variations[variationType],
      originalVariation = variations.filter((variation) => variation.id === variationId)[0];
    originalVariation.amount = parseInt(e.target.value);
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
            accounts={ this.state.accounts }
            addVariation={ (e, variationType) => this.addVariation(e, variationType) }
            deleteVariation={ (variationType, variationID) => this.deleteVariation(variationType, variationID) }
            changeVariationAccount={ (e, variationType, variationId) => this.changeVariationAccount(e, variationType, variationId) }
            changeVariationAmount={ (e, variationType, variationId) => this.changeVariationAmount(e, variationType, variationId) }
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
  getVariationsList(variationType) {
    return this.props.variations[variationType].map((variation) => (
        <Variation
          key={ variation.id }
          variationType={ variationType }
          deleteVariation={ (variationType, variationID) => this.props.deleteVariation(variationType, variationID) }
          changeVariationAccount={
            (e, variationType, variationId) => {
              this.props.changeVariationAccount(e, variationType, variationId)
            }
          }
          changeVariationAmount={
            (e, variationType, variationId) => {
              this.props.changeVariationAmount(e, variationType, variationId)
            }
          }
          editMode={ this.props.editMode }
          accounts={ this.props.accounts }
          {...variation}
        />
      )
    );
  }

  render() {
    const debitVariations = this.getVariationsList(DEBIT);
    const creditVariations = this.getVariationsList(CREDIT);

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
    let valueColumn;

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
        <option key={ account.id } value={ account.id }>
          { account.type }: { account.full_name }
        </option>
      ));
      accountColumn = (
        <select
          style={{ width: "70%" }}
          className={ "form-control form-control-sm " + accountColumnClass } onChange={ () => null }
          onChange={ (e) => this.props.changeVariationAccount(e, this.props.variationType, this.props.id) }
          value={ this.props.account_id.toString() }
        >
          { accountColumnOptions }
        </select>
      );
      valueColumn = (
        <td>
          <input
            type="text"
            className="form-control form-control-sm"
            value={ this.props.amount }
            onChange={ (e) => this.props.changeVariationAmount(e, this.props.variationType, this.props.id) }
          />
        </td>
      );
    } else {
      accountColumn = (
        <span className={ accountColumnClass }>
          <a href={ this.props.account_url }>{ this.props.account_name }</a>
        </span>
      );
      valueColumn = (
        <td>
          <span className="float-right">{ this.props.amount }</span>
        </td>
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
