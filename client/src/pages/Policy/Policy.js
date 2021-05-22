import React from 'react';
import PropTypes from 'prop-types';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import IconButton from '@material-ui/core/IconButton';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import FormGroup from '@material-ui/core/FormGroup';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

// Lodash
import map from 'lodash/map';
import find from 'lodash/find';
import forOwn from 'lodash/forOwn';

// Project
import PolicyTags from '../../modules/components/PolicyTags';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import PolicyService from '../../modules/api/policy';
import ScheduleService from '../../modules/api/schedule';
import { getDefaultPolicy } from '../../modules/utils/policy';

const styles = (theme) => ({
  root: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing(2),
  },
  textField: {
    width: 550,
    marginBottom: theme.spacing(3),
    marginRight: theme.spacing(2),
  },
  formControl: {
    width: 550,
    marginBottom: theme.spacing(4),
  },
});

class Policy extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      policy: null,
      schedules: null,
      isLoading: false,

      nameError: false,
      scheduleError: false,
      projectsError: false,
      tagsError: [],

      showBackendError: false,
      backendErrorTitle: null,
      backendErrorMessage: null,
    };

    this.policyService = new PolicyService();
    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const { match } = this.props;
      this.setState({ isLoading: true });
      const schedules = await this.scheduleService.list();
      if (!schedules || !schedules.length) {
        throw new Error('Create at least one Schedule first');
      }

      let policy;
      if (match.params.policy) {
        policy = await this.policyService.get(match.params.policy);
      } else {
        policy = getDefaultPolicy();
        if (schedules && schedules.length) {
          policy.schedulename = schedules[0].name;
        }
      }
      this.setState({
        policy,
        schedules,
        isLoading: false,
      });
    } catch (error) {
      this.handleBackendError(
        'Loading Failed:',
        error.message,
        '/policies/browser'
      );
    }
  }

  handleChange = (name) => (event) => {
    const { policy } = this.state;
    policy[name] = event.target.value;
    this.setState({ policy });
  };

  handleChangeTags = (tags, shouldUpdateErrors) => {
    const { policy } = this.state;
    policy.tags = tags;
    if (shouldUpdateErrors) {
      const tagsError = this.getTagsError();
      this.setState({ policy, tagsError });
    } else {
      this.setState({ policy });
    }
  };

  handleChangeProjects = (event) => {
    const { policy } = this.state;
    policy.projects = event.target.value.replace(/\s/g, '').split(',');
    this.setState({
      policy,
    });
  };

  getTagsError = () => {
    const { policy } = this.state;
    const tagsKeyRe = /(^[a-z][a-z0-9_-]*[a-z0-9]$)|(^@app_engine_flex$)/; // Add app App Engine identifier
    const tagsValRe =
      /(^[a-z][a-z0-9_-]*[a-z0-9]$)|(^[a-z][a-z0-9_-]*:[a-z0-9_-]+$)/; // Add app App Engine identifier
    let tagsError = [];
    for (let i = 0; i < policy.tags.length; i++) {
      tagsError.push([false, false]);
      forOwn(policy.tags[i], (value, key) => {
        if (!tagsKeyRe.test(key)) {
          tagsError[i][0] = true;
        }
        if (!tagsValRe.test(value)) {
          tagsError[i][1] = true;
        }
      });
    }
    return tagsError;
  };

  handleSubmit = async (event) => {
    try {
      const { history } = this.props;
      const { policy } = this.state;

      const nameRe = /^[a-zA-Z][\w-]*[a-zA-Z0-9]$/;
      const projectsRe = /^[a-z][a-z0-9-]+[a-z0-9]$/;

      let nameError = false;
      let projectsError = !policy.projects.length;
      const scheduleError = !policy.schedulename;
      const tagsError = this.getTagsError();

      if (!nameRe.test(policy.name)) {
        nameError = true;
      }

      for (let i = 0; i < policy.projects.length && !projectsError; i++) {
        if (!projectsRe.test(policy.projects[i])) {
          projectsError = true;
        }
      }

      if (
        nameError ||
        projectsError ||
        scheduleError ||
        find(tagsError, (tagErrors) => tagErrors[0] || tagErrors[1])
      ) {
        this.setState({
          nameError,
          scheduleError,
          projectsError,
          tagsError,
        });
      } else {
        this.setState({ isLoading: true });
        await this.policyService.add(policy);
        this.setState({ isLoading: false });
        history.push('/policies/browser');
      }
    } catch (error) {
      this.handleBackendError('Update failed:', error.message);
    }
  };

  handleRequestCancel = (event) => {
    const { history } = this.props;
    history.goBack();
  };

  handleBackendError = (title, message, exitPage) => {
    this.setState({
      backendErrorTitle: title,
      backendErrorMessage: message,
      showBackendError: true,
      isLoading: false,
      exitPage,
    });
  };

  handleErrorClose = () => {
    const { history } = this.props;
    const { exitPage } = this.state;
    this.setState({
      showBackendError: false,
      isLoading: false,
    });
    if (exitPage) {
      history.push(exitPage);
    }
  };

  render() {
    const { classes, edit } = this.props;
    const {
      policy,
      schedules,
      nameError,
      scheduleError,
      projectsError,
      tagsError,
      isLoading,
      backendErrorTitle,
      backendErrorMessage,
      showBackendError,
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

          {edit ? (
            <Typography variant="subtitle1" color="primary">
              Edit policy {policy ? policy.name : ''}
            </Typography>
          ) : (
            <Typography variant="subtitle1" color="primary">
              Create a policy
            </Typography>
          )}
        </AppPageActions>

        <AppPageContent
          showBackendError={showBackendError}
          backendErrorTitle={backendErrorTitle}
          backendErrorMessage={backendErrorMessage}
          onBackendErrorClose={this.handleErrorClose}
          showLoadingSpinner={isLoading}
        >
          {policy && (
            <div>
              <FormGroup row={false}>
                <TextField
                  disabled={edit}
                  id="policy-name"
                  error={nameError}
                  helperText="Required. May only contain letters, digits and underscores. It may not end with an underscore."
                  label="Policy Name (ID)"
                  className={classes.textField}
                  value={this.state.policy.name}
                  onChange={this.handleChange('name')}
                  margin="none"
                  autoFocus
                  InputLabelProps={{
                    shrink: true,
                  }}
                />

                <TextField
                  id="policy-displayname"
                  helperText="Optional. Text to display instead of Name (ID)"
                  label="Policy Displayname"
                  className={classes.textField}
                  value={this.state.policy.displayname}
                  onChange={this.handleChange('displayname')}
                  margin="none"
                  InputLabelProps={{
                    shrink: true,
                  }}
                />

                <FormControl className={classes.formControl}>
                  <InputLabel
                    shrink
                    error={scheduleError}
                    htmlFor="schedule-input"
                  >
                    Schedule name
                  </InputLabel>
                  <Select
                    error={scheduleError}
                    native
                    value={this.state.policy.schedulename}
                    onChange={this.handleChange('schedulename')}
                    inputProps={{
                      id: 'schedule-input',
                    }}
                  >
                    {map(schedules, (schedule) => (
                      <option key={schedule.name} value={schedule.name}>
                        {schedule.displayName || schedule.name}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <TextField
                  id="projects-list"
                  error={projectsError}
                  helperText="Separated by comma"
                  label="Projects"
                  className={classes.textField}
                  value={policy.projects.join(',')}
                  onChange={this.handleChangeProjects}
                  margin="none"
                  InputLabelProps={{
                    shrink: true,
                  }}
                />

                <PolicyTags
                  error={tagsError}
                  tags={policy.tags}
                  onChange={this.handleChangeTags}
                />
              </FormGroup>

              <Button
                className={classes.button}
                variant="contained"
                color="primary"
                size="small"
                onClick={this.handleSubmit}
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
            </div>
          )}
        </AppPageContent>
      </div>
    );
  }
}

Policy.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Policy);
