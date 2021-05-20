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
import { getDefaultSchedule } from '../../modules/utils/schedule';

const styles = (theme) => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing(2),
  },
  textField: {
    minWidth: 250,
    marginBottom: theme.spacing(3),
    marginRight: theme.spacing(2),
  },
});

class ScheduleCreate extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: getDefaultSchedule(),
      nameError: false,
      backendError: false,
      backendErrorMessage: 'unspecified error',
      timezones: [],
    };

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const response = await this.scheduleService.timezones();
      this.setState({
        timezones: response.Timezones,
      });
    } catch (ex) {
      console.error(ex);
    }
  }

  handleChange = (name) => (event) => {
    const { schedule } = this.state;
    schedule[name] = event.target.value;
    this.setState({ schedule });
  };

  handleChangeTimezone = (value) => {
    const { schedule } = this.state;
    schedule.timezone = value;
    this.setState({ schedule });
  };

  handleScheduleChange = (nextSchedule) => {
    this.setState({
      schedule: nextSchedule,
    });
  };

  handleCreate = async (event) => {
    try {
      const { history } = this.props;
      const { schedule } = this.state;
      const nameRe = /^[a-zA-Z][\w-]*[a-zA-Z0-9]$/;
      if (!nameRe.test(schedule.name)) {
        this.setState({
          nameError: true,
        });
        return;
      }
      await this.scheduleService.add(schedule);
      history.push('/schedules/browser');
    } catch (ex) {
      this.handleBackendError(ex.message);
    }
  };

  handleRequestCancel = (event) => {
    const { history } = this.props;
    history.goBack();
  };

  handleBackendError = (errorMessage) => {
    this.setState({
      backendErrorMessage: errorMessage,
      backendError: true,
    });
  };

  handleBackendErrorClose = () => {
    this.setState({ backendError: false });
  };

  render() {
    const { classes } = this.props;
    const { schedule, timezones, nameError } = this.state;

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
            Create a schedule
          </Typography>
        </AppPageActions>

        <AppPageContent>
          <TextField
            id="schedule-name"
            error={nameError}
            helperText="Required. May only contain letters, digits and underscores. It may not end with an underscore."
            placeholder="Schedule Name (ID)"
            className={classes.textField}
            value={schedule.name}
            onChange={this.handleChange('name')}
            margin="none"
            autoFocus
          />

          <TextField
            id="schedule-displayname"
            helperText="Optional. Text to display instead of Schedule Name (ID)"
            placeholder="Schedule Displayname"
            className={classes.textField}
            value={schedule.displayname}
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
            onClick={this.handleCreate}
          >
            Create
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

          <Dialog
            open={this.state.backendError}
            onClose={this.handleBackendErrorClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
          >
            <DialogTitle id="alert-dialog-title">
              {'Creation Failed:'}
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
        </AppPageContent>
      </div>
    );
  }
}

export default withStyles(styles)(ScheduleCreate);
