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
import Input, { InputLabel } from 'material-ui/Input';
import { MenuItem } from 'material-ui/Menu';
import { FormControl, FormHelperText } from 'material-ui/Form';
import Select from 'material-ui/Select';

// Lodash
import map from 'lodash/map';
// import find from 'lodash/find';
// import flatten from 'lodash/flatten';

// Project
import ScheduleTimeTable from '../../modules/components/ScheduleTimeTable';
import ScheduleTimeZone from '../../modules/components/ScheduleTimeZone';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import ScheduleService from '../../modules/api/schedule';
import { getDefaultSchedule } from '../../modules/utils/schedule';

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
  },
  formControl: {
    marginBottom: theme.spacing.unit * 3,
    minWidth: 250,
  }
});

class ScheduleCreate extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: getDefaultSchedule(),
      timezones: [],
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const response = await this.scheduleService.timezones();
      this.setState({
        timezones: response.Timezones
      });
    } catch (ex) {
      console.error(ex);
    }
  }

  handleChange = name => event => {
    const { schedule } = this.state;
    schedule[name] = event.target.value;
    this.setState({ schedule });
  };

  handleChangeTimezone = value => {
    const { schedule } = this.state;
    schedule.timezone = value;
    this.setState({ schedule });
  };

  handleScheduleChange = nextSchedule => {
    this.setState({
      schedule: nextSchedule
    });
  }

  handleCreate = event => {
    try {
      const { history } = this.props;
      const { schedule } = this.state;
      const response = this.scheduleService.add(schedule);
      console.log(response);
      history.push('/schedules/browser');

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
    const { schedule, timezones } = this.state;

    return (
      <div className={classes.root}>
        <AppPageActions>
          <IconButton color="primary" aria-label="Back" onClick={this.handleRequestCancel}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="subheading" color="primary">
            Create a schedule
          </Typography>
        </AppPageActions>


        <AppPageContent>

          <TextField
            id="schedule-name"
            error={false}
            helperText=""
            placeholder="Schedule name"
            className={classes.textField}
            value={this.state.schedule.name}
            onChange={this.handleChange('name')}
            margin="none"
          />

          <ScheduleTimeZone timezones={timezones} onSelect={this.handleChangeTimezone} />

          <ScheduleTimeTable schedule={this.state.schedule} onScheduleChange={this.handleScheduleChange} />

          <Button className={classes.button} variant="raised" color="primary" size="small" onClick={this.handleCreate}>
            Create
          </Button>
          <Button className={classes.button} color="primary" size="small" onClick={this.handleRequestCancel}>
            Cancel
          </Button>
        </AppPageContent>
      </div >
    )
  }
}

export default withStyles(styles)(ScheduleCreate);
