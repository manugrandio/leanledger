import React, { Component } from "react";


const DEBIT = "debit";
const CREDIT = "credit";


class Record extends Component {
  render() {
    const record = {
      is_balanced: true,
      date: "2019-12-31",
      variations: {
        debit: [
          {
            id: 1,
            accountName: "cash",
            accountURL: "http://localhost:8000/ledger/1/account/2/",
            amount: 100
          },
        ],
        credit: [
          {
            id: 2,
            accountName: "expense one",
            accountURL: "http://localhost:8000/ledger/1/account/3/",
            amount: 50
          },
          {
            id: 3,
            accountName: "expense two",
            accountURL: "http://localhost:8000/ledger/1/account/4/",
            amount: 50
          },
        ],
      },
    };
    return(
      <div className="card mt-3 shadow-sm">
        <RecordHeader {...record}/>
        <RecordBody {...record}/>
      </div>
    );
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
            <a href={ this.props.accountURL }>{ this.props.accountName }</a>
          </span>
        </td>
        { this.props.variationType === DEBIT ? valueColumn : emptyColumn }
        { this.props.variationType === DEBIT ? emptyColumn : valueColumn }
      </tr>
    );
  }
}


export default Record;
