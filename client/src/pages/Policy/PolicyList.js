import React from 'react';

// Recompose
import { compose } from 'recompose';

// Router
import {
  withRouter,
} from 'react-router-dom';

// Material UI
import { withStyles } from 'material-ui/styles';
import Table, { TableBody, TableCell, TableHead, TableRow, TableSortLabel } from 'material-ui/Table';
import Tooltip from 'material-ui/Tooltip';
import Button from 'material-ui/Button';
import Checkbox from 'material-ui/Checkbox';
import AddIcon from 'material-ui-icons/Add';
import RefreshIcon from 'material-ui-icons/Refresh';
import EditIcon from 'material-ui-icons/Edit';
import DeleteIcon from 'material-ui-icons/Delete';

// Lodash
import map from 'lodash/map';
import indexOf from 'lodash/indexOf';

// Project
import PolicyService from '../../modules/api/policy';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';

const styles = theme => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing.unit * 2,
  },
  leftIcon: {
    marginRight: theme.spacing.unit,
  },
  link: {
    '&:hover': {
      textDecoration: 'underline',
      cursor: 'pointer'
    }
  },
  checkboxCell: {
    width: 48
  }
});

class PolicyList extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      policies: [],
      selected: [],
      order: 'asc'
    }

    this.policyService = new PolicyService();
  }

  componentDidMount() {
    this.refreshList();
    // this.refrestInterval = setInterval(this.refreshList, 10000);
  }

  componentWillUnmount() {
    // clearInterval(this.refrestInterval);
  }

  handleRequestSort = event => {
    this.setState((prevState, props) => {
      let order = 'desc'
      if (prevState.order === 'desc') {
        order = 'asc';
      }

      const policies =
        order === 'desc'
          ? prevState.policies.sort((a, b) => b < a ? -1 : 1)
          : prevState.policies.sort((a, b) => a < b ? -1 : 1);

      return {
        policies,
        order
      }
    });
  }

  handleClickNavigate = path => event => {
    const { history } = this.props;
    history.push(path);
  }

  handleClickRefresh = event => {
    this.refreshList();
  }

  refreshList = async () => {
    const policies = await this.policyService.list();
    this.setState({
      policies
    });
  }

  handleClick = (event, policy) => {
    const { selected } = this.state;
    const selectedIndex = indexOf(selected, policy);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, policy);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    this.setState({ selected: newSelected });
  };

  handleSelectAllClick = (event, checked) => {
    if (checked) {
      this.setState({ selected: this.state.policies });
    } else {
      this.setState({ selected: [] });
    }
  };

  handleDeleteClick = async event => {
    try {
      const { selected } = this.state;
      if (selected.length > 0) {
        const promises = [];
        selected.forEach(policy => {
          promises.push(this.policyService.delete(policy))
        })
        const responses = await Promise.all(promises);
        console.log(responses);
        this.setState({
          selected: []
        })
      }
    } catch (ex) {
      console.error(ex);
    }
  }

  render() {
    const { classes } = this.props;
    const { policies, selected, order } = this.state;

    const rowCount = policies.length;
    const numSelected = selected.length;

    return (
      <div className={classes.root}>
        <AppPageActions>
          <Button className={classes.button} color="primary" size="small" onClick={this.handleClickNavigate(`/policies/create`)}>
            <AddIcon className={classes.leftIcon} />
            Create Policy
          </Button>
          <Button className={classes.button} color="primary" size="small" onClick={this.handleClickRefresh}>
            <RefreshIcon className={classes.leftIcon} />
            Refresh
          </Button>
          <Button className={classes.button} color="primary" size="small" disabled={selected.length !== 1} onClick={this.handleClickNavigate(`/policies/browser/${selected[0]}`)}>
            <EditIcon className={classes.leftIcon} />
            Edit
          </Button>
          <Button className={classes.button} color="primary" size="small" disabled={selected.length < 1} onClick={this.handleDeleteClick}>
            <DeleteIcon className={classes.leftIcon} />
            Delete
          </Button>
        </AppPageActions>

        <AppPageContent>
          <Table className={classes.table}>
            <TableHead>
              <TableRow>
                <TableCell padding="none" className={classes.checkboxCell}>
                  <Checkbox
                    indeterminate={numSelected > 0 && numSelected < rowCount}
                    checked={rowCount > 0 && numSelected === rowCount}
                    onChange={this.handleSelectAllClick}
                  />
                </TableCell>
                <TableCell sortDirection={order}>
                  <Tooltip
                    title={order === 'desc' ? 'descending' : 'ascending'}
                    placement="bottom-start"
                    enterDelay={500}
                  >
                    <TableSortLabel
                      active
                      direction={order}
                      onClick={this.handleRequestSort}
                    >
                      Policies
                  </TableSortLabel>
                  </Tooltip></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>

              {
                map(policies, policy => {
                  const isSelected = indexOf(selected, policy) !== -1;
                  return (
                    <TableRow
                      hover
                      role="checkbox"
                      aria-checked={isSelected}
                      tabIndex={-1}
                      key={policy}
                      selected={isSelected}
                    >
                      <TableCell padding="none" className={classes.checkboxCell}>
                        <Checkbox checked={isSelected} onClick={event => this.handleClick(event, policy)} />
                      </TableCell>

                      <TableCell >
                        <span onClick={this.handleClickNavigate(`/policies/browser/${policy}`)} className={classes.link}>{policy}</span>
                      </TableCell>
                    </TableRow>
                  )
                })
              }

            </TableBody>
          </Table>
        </AppPageContent>
      </div>
    )
  }
}

export default compose(
  withRouter,
  withStyles(styles),
)(PolicyList);
