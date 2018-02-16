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
import List, {
  ListItem,
  ListSubheader,
  ListItemText,
} from 'material-ui/List';

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
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const schedules = await this.scheduleService.list();
    this.setState({
      schedules
    });
  }

  render() {
    const { classes, history } = this.props;
    const { schedules } = this.state;

    return (
      <div className={classes.root}>
        <List
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
        </List>

      </div>
    )
  }
}

export default compose(
  withRouter,
  withStyles(styles),
)(ScheduleList);
