import React, { Component } from "react";


const DEBIT = "debit";
const CREDIT = "credit";


class Record extends Component {
  constructor(props) {
    super(props);
    this.state = {record: null};
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

  render() {
    if (this.state.record === null) {
      return <p className="mt-3">Loading...</p>;
    } else {
      return (
        <div className="card mt-3 shadow-sm">
          <RecordHeader {...this.state.record}/>
          <RecordBody {...this.state.record}/>
        </div>
      );
    }
  }
}


class RecordHeader extends Component {
  render() {
    let balancedState;
    if (this.props.is_balanced) {
      balancedState = <span className="float-right badge badge-success align-bottom">ok</span>;
    } else {
      balancedState = <span className="float-right badge badge-danger">unbalanced</span>;
    }
    return (
      <div className="card-header">
        <strong>{ this.props.date }</strong>
        <em className="mr-3 float-right">{ this.props.description }</em>
        { balancedState }
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
        {...variation}
      />
    ));
    const creditVariations = this.props.variations.credit.map((variation) => (
      <Variation
        key={ variation.id }
        variationType={ CREDIT }
        {...variation}
      />
    ));
    return (
      <div className="card-body">
        <table className="table table-borderless table-sm mb-0">
          <tbody>
            { debitVariations }
            { creditVariations }
          </tbody>
        </table>
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
    return (
      <tr>
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