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
        <Typography variant="subheading" color="textSecondary">
          Schedule List:
        </Typography>

        {
          map(schedules, schedule =>
            <Typography key={schedule} variant="body2" color="textSecondary" className={classes.listItem} onClick={() => history.push(`/schedules/${schedule}`)}>
              {schedule}
            </Typography>
          )
        }
        
      </div>
    )
  }
}

export default compose(
  withRouter,
  withStyles(styles),
)(ScheduleList);
