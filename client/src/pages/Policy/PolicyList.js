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

import AddIcon from 'material-ui-icons/Add';
import RefreshIcon from 'material-ui-icons/Refresh';
import DeleteIcon from 'material-ui-icons/Delete';

// Lodash
import map from 'lodash/map';

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
});

class PolicyList extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      policies: [],
      order: 'asc'
    }

    this.policyService = new PolicyService();
  }

  componentDidMount() {
    this.refreshList();
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


  render() {
    const { classes } = this.props;
    const { policies, order } = this.state;

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
          <Button className={classes.button} color="primary" size="small" disabled>
            <DeleteIcon className={classes.leftIcon} />
            Delete
          </Button>
        </AppPageActions>

        <AppPageContent>
          <Table className={classes.table}>
            <TableHead>
              <TableRow>
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
              {map(policies, policy =>
                <TableRow key={policy} hover >
                  <TableCell onClick={this.handleClickNavigate(`/policies/browser/${policy}`)}>
                    {policy}
                  </TableCell>
                </TableRow>
              )}
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
