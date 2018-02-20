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
import ScheduleService from '../../modules/api/schedule';
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

class ScheduleList extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedules: [],
      selected: [],
      order: 'asc'
    }

    this.scheduleService = new ScheduleService();
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

  handleClickNavigate = path => event => {
    const { history } = this.props;
    history.push(path);
  }

  handleClickRefresh = event => {
    this.refreshList();
  }

  refreshList = async () => {
    const schedules = await this.scheduleService.list();
    this.setState({
      schedules
    });
  }

  handleClick = (event, schedule) => {
    const { selected } = this.state;
    const selectedIndex = indexOf(selected, schedule);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, schedule);
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
      this.setState({ selected: this.state.schedules });
    } else {
      this.setState({ selected: [] });
    }
  };

  handleDeleteClick = async event => {
    try {
      const { selected } = this.state;
      if (selected.length > 0) {
        const schedules = [];
        selected.forEach(schedule => {
          schedules.push(this.scheduleService.delete(schedule))
        })
        const responses = await Promise.all(schedules);
        responses.forEach(async response => {
          if (!response.ok) {
            const errorMsg = await response.text();
            console.log(errorMsg);
          }
        });
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
    const { schedules, selected, order } = this.state;

    const rowCount = schedules.length;
    const numSelected = selected.length;

    return (
      <div className={classes.root}>
        <AppPageActions>
          <Button className={classes.button} color="primary" size="small" onClick={this.handleClickNavigate(`/schedules/create`)}>
            <AddIcon className={classes.leftIcon} />
            Create Schedule
          </Button>
          <Button className={classes.button} color="primary" size="small" onClick={this.handleClickRefresh}>
            <RefreshIcon className={classes.leftIcon} />
            Refresh
          </Button>
          <Button className={classes.button} color="primary" size="small" disabled={selected.length !== 1} onClick={this.handleClickNavigate(`/schedules/browser/${selected[0]}`)}>
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
                      Schedules
                  </TableSortLabel>
                  </Tooltip></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {
                map(schedules, schedule => {
                  const isSelected = indexOf(selected, schedule) !== -1;
                  return (
                    <TableRow
                      hover
                      role="checkbox"
                      aria-checked={isSelected}
                      tabIndex={-1}
                      key={schedule}
                      selected={isSelected}
                    >
                      <TableCell padding="none" className={classes.checkboxCell}>
                        <Checkbox checked={isSelected} onClick={event => this.handleClick(event, schedule)} />
                      </TableCell>

                      <TableCell >
                        <span onClick={this.handleClickNavigate(`/schedules/browser/${schedule}`)} className={classes.link}>{schedule}</span>
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
)(ScheduleList);
