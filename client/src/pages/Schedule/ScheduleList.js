import React from 'react';

// Recompose
import { compose } from 'recompose';

// Router
import {
  withRouter,
} from 'react-router-dom';


// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
import Tooltip from 'material-ui/Tooltip';
// import List, {
//   ListItem,
//   ListSubheader,
//   ListItemText,
// } from 'material-ui/List';

import Table, { TableBody, TableCell, TableHead, TableRow, TableSortLabel } from 'material-ui/Table';


// Lodash
import map from 'lodash/map';

// Project
import ScheduleService from '../../modules/api/schedule';

const styles = theme => ({
  root: {
    padding: theme.spacing.unit,
  },
  listItem: {
    cursor: 'pointer',
  }
});

class ScheduleList extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedules: [],
      order: 'asc'
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const schedules = await this.scheduleService.list();
    this.setState({
      schedules
    });
  }

  handleRequestSort = event => {
    this.setState((prevState, props) => {
      let order = 'desc'
      if (prevState.order === 'desc') {
        order = 'asc';
      }

      const schedules =
        order === 'desc'
          ? prevState.schedules.sort((a, b) => b < a ? -1 : 1)
          : prevState.schedules.sort((a, b) => a < b ? -1 : 1);

      return {
        schedules,
        order
      }
    });
  }

  render() {
    const { classes, history } = this.props;
    const { schedules, order } = this.state;

    return (
      <div className={classes.root}>

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
                    Schedules
                  </TableSortLabel>
                </Tooltip></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {map(schedules, schedule =>
              <TableRow key={schedule} hover >
                <TableCell onClick={() => history.push(`/schedules/${schedule}`)}>
                  {schedule}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>


        {/* <List
          component="nav"
          subheader={<ListSubheader component="div">Schedule List</ListSubheader>}
        >
          {
            map(schedules, schedule =>
              <ListItem key={schedule} button onClick={() => history.push(`/schedules/${schedule}`)}>
                <ListItemText
                  primary={schedule}
                  secondary=""
                />
              </ListItem>

            )
          }
        </List> */}

      </div>
    )
  }
}

export default compose(
  withRouter,
  withStyles(styles),
)(ScheduleList);
