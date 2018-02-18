import React from 'react';
// import classNames from 'classnames';

// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
// import Paper from 'material-ui/Paper';
import Button from 'material-ui/Button';
import ArrowBackIcon from 'material-ui-icons/ArrowBack';
import IconButton from 'material-ui/IconButton';
import TextField from 'material-ui/TextField';

// Lodash
// import set from 'lodash/set';
// import find from 'lodash/find';
// import flatten from 'lodash/flatten';

// Project
import ScheduleTimeTable from '../../modules/components/ScheduleTimeTable';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import ScheduleService from '../../modules/api/schedule';

const styles = theme => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing.unit * 2,
  },
  textField: {
    width: 250,
    marginBottom: theme.spacing.unit * 3,
  }
});

class ScheduleEdit extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: null
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    try {
      const schedule = await this.scheduleService.get(match.params.schedule);
      console.log(schedule);
      this.setState({
        schedule
      });
    } catch (ex) {
      console.error(ex);
    }
  }

  handleScheduleChange = nextSchedule => {
    this.setState({
      schedule: nextSchedule
    });
  }

  handleCreate = async event => {
    try {
      const { schedule } = this.state;
      console.log(schedule);
      const response = await this.scheduleService.add(schedule);
      console.log(response)
    } catch (ex) {
      console.error(ex)
    }
  }

  handleRequestCancel = event => {
    const { history } = this.props;
    history.goBack();
  }


  render() {
    const { classes } = this.props;
    const { schedule } = this.state;

    if (schedule) {
      return (
        <div className={classes.root}>
          <AppPageActions>
            <IconButton color="primary" aria-label="Back" onClick={this.handleRequestCancel}>
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="subheading" color="primary">
              Edit schedule {schedule.name}
            </Typography>
          </AppPageActions>

          <AppPageContent>
            <TextField
              disabled
              id="schedule-name"
              className={classes.textField}
              value={schedule.name}
              margin="none"
            />

            {this.state.schedule && <ScheduleTimeTable schedule={this.state.schedule} onScheduleChange={this.handleScheduleChange} />}

            <Button className={classes.button} variant="raised" color="primary" size="small" onClick={this.handleCreate}>
              Save
            </Button>
            <Button className={classes.button} color="primary" size="small" onClick={this.handleRequestCancel}>
              Cancel
            </Button>
          </AppPageContent>
        </div >
      )
    } else {
      return (<div></div>)
    }
  }
}

export default withStyles(styles)(ScheduleEdit);
