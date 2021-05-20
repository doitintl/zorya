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
import CircularProgress from '@material-ui/core/CircularProgress';

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
    width: 450,
    marginBottom: theme.spacing(3),
    marginRight: theme.spacing(2),
  },
  formControl: {
    width: 450,
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
    };

    this.policyService = new PolicyService();
    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const { match } = this.props;
      this.setState({ isLoading: true });
      const schedules = await this.scheduleService.list();
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
    } catch (ex) {
      console.error(ex);
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
    const tagsRe = /^[a-z][a-z0-9_-]*[a-z0-9]$/;
    let tagsError = [];
    for (let i = 0; i < policy.tags.length; i++) {
      tagsError.push([false, false]);
      forOwn(policy.tags[i], (value, key) => {
        if (!tagsRe.test(key)) {
          tagsError[i][0] = true;
        }
        if (!tagsRe.test(value)) {
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
        const response = await this.policyService.add(policy);
        history.push('/policies/browser');
      }
    } catch (ex) {
      console.error(ex);
    }
  };

  handleRequestCancel = (event) => {
    const { history } = this.props;
    history.goBack();
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
    } = this.state;

    if (policy) {
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
                Edit policy {policy.name}
              </Typography>
            ) : (
              <Typography variant="subtitle1" color="primary">
                Create a policy
              </Typography>
            )}
          </AppPageActions>

          <AppPageContent>
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
                label="Policy Displayname (optional)"
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
          </AppPageContent>
        </div>
      );
    } else {
      return this.state.isLoading ? (
        <AppPageContent>
          <CircularProgress />
        </AppPageContent>
      ) : (
        <div />
      );
    }
  }
}

Policy.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Policy);
