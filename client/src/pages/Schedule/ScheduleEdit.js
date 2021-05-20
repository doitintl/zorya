import React from 'react';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

// Project
import ScheduleTimeTable from '../../modules/components/ScheduleTimeTable';
import ScheduleTimeZone from '../../modules/components/ScheduleTimeZone';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
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
      backendError: false,
      backendErrorTitle: 'An Error Occurred:',
      backendErrorMessage: 'Unspecified Error',
    };

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    try {
      const schedule = await this.scheduleService.get(match.params.schedule);
      const timezones = await this.scheduleService.timezones();
      this.setState({
        schedule,
        timezones: timezones.Timezones,
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

  handleBackendError = (errorTitle, errorMessage) => {
    this.setState({
      backendErrorTitle: errorTitle,
      backendErrorMessage: errorMessage,
      backendError: true,
    });
  };

  handleBackendErrorClose = () => {
    this.setState({ backendError: false });
  };

  render() {
    const { classes } = this.props;
    const { schedule, timezones } = this.state;

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
        <Dialog
          open={this.state.backendError}
          onClose={this.handleBackendErrorClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            {this.state.backendErrorTitle}
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              {this.state.backendErrorMessage}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={this.handleBackendErrorClose}
              color="primary"
              autoFocus
            >
              OK
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    );
  }
}

export default withStyles(styles)(ScheduleEdit);
