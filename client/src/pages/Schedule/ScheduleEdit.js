import React from 'react';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@material-ui/core/TextField';
import CircularProgress from '@material-ui/core/CircularProgress';

// Project
import ScheduleTimeTable from '../../modules/components/ScheduleTimeTable';
import ScheduleTimeZone from '../../modules/components/ScheduleTimeZone';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import ErrorAlert from '../../modules/components/ErrorAlert';
import ScheduleService from '../../modules/api/schedule';

const styles = (theme) => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing(2),
  },
  textField: {
    width: 350,
    marginBottom: theme.spacing(3),
  },
});

class ScheduleEdit extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: null,
      isLoading: false,
      showBackendError: false,
      backendErrorTitle: null,
      backendErrorMessage: null,
    };

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    this.setState({ isLoading: true });
    try {
      const schedule = await this.scheduleService.get(match.params.schedule);
      const timezones = await this.scheduleService.timezones();
      this.setState({
        schedule,
        timezones: timezones.Timezones,
        isLoading: false,
      });
    } catch (error) {
      this.handleBackendError('Loading Failed:', error.message);
    }
  }

  handleChange = (name) => (event) => {
    const { schedule } = this.state;
    schedule[name] = event.target.value;
    this.setState({ schedule });
  };

  handleScheduleChange = (nextSchedule) => {
    this.setState({
      schedule: nextSchedule,
    });
  };

  handleChangeTimezone = (value) => {
    const { schedule } = this.state;
    schedule.timezone = value;
    this.setState({ schedule });
  };

  handleSave = async (event) => {
    try {
      const { history } = this.props;
      const { schedule } = this.state;
      await this.scheduleService.add(schedule);
      history.push('/schedules/browser');
    } catch (error) {
      this.handleBackendError('Saving failed:', error.message);
    }
  };

  handleRequestCancel = (event) => {
    const { history } = this.props;
    history.goBack();
  };

  handleBackendError = (title, message) => {
    this.setState({
      backendErrorTitle: title,
      backendErrorMessage: message,
      showBackendError: true,
      isLoading: false,
    });
  };

  handleErrorClose = () => {
    this.setState({
      showBackendError: false,
      isLoading: false,
    });
  };

  render() {
    const { classes } = this.props;
    const {
      schedule,
      timezones,
      isLoading,
      showBackendError,
      backendErrorTitle,
      backendErrorMessage,
    } = this.state;

    return (
      <div className={classes.root}>
        <AppPageActions>
          <IconButton
            color="primary"
            aria-label="Back"
            onClick={this.handleRequestCancel}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="subtitle1" color="primary">
            Edit schedule {schedule ? schedule.name : ''}
          </Typography>
        </AppPageActions>
        {isLoading && <CircularProgress />}
        {schedule && (
          <AppPageContent>
            <TextField
              disabled
              id="schedule-name"
              className={classes.textField}
              label="Schedule Name (ID)"
              value={schedule.name}
              margin="none"
            />

            <TextField
              id="schedule-displayname"
              className={classes.textField}
              value={schedule.displayname}
              label="Schedule Display-Name"
              onChange={this.handleChange('displayname')}
              margin="none"
            />

            <ScheduleTimeZone
              selected={schedule.timezone}
              timezones={timezones}
              onSelect={this.handleChangeTimezone}
            />

            <ScheduleTimeTable
              schedule={schedule}
              onScheduleChange={this.handleScheduleChange}
            />

            <Button
              className={classes.button}
              variant="contained"
              color="primary"
              size="small"
              onClick={this.handleSave}
            >
              Save
            </Button>
            <Button
              className={classes.button}
              variant="outlined"
              color="primary"
              size="small"
              onClick={this.handleRequestCancel}
            >
              Cancel
            </Button>
          </AppPageContent>
        )}
        <ErrorAlert
          showError={showBackendError}
          errorTitle={backendErrorTitle}
          errorMessage={backendErrorMessage}
          onClose={this.handleErrorClose}
        />
      </div>
    );
  }
}

export default withStyles(styles)(ScheduleEdit);
