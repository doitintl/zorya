import React from 'react';
import PropTypes from 'prop-types';

// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
import Button from 'material-ui/Button';
import ArrowBackIcon from 'material-ui-icons/ArrowBack';
import IconButton from 'material-ui/IconButton';
import TextField from 'material-ui/TextField';

import { InputLabel } from 'material-ui/Input';
import { FormGroup, FormControl } from 'material-ui/Form';
import Select from 'material-ui/Select';


// Lodash
import map from 'lodash/map';

// Project
import PolicyProjects from '../../modules/components/PolicyProjects';
import PolicyTags from '../../modules/components/PolicyTags';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import PolicyService from '../../modules/api/policy';
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
  },
  formControl: {
    width: 250,
    marginBottom: theme.spacing.unit * 3,
  },
});

class PolicyEdit extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      policy: null
    }

    this.policyService = new PolicyService();
    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const { match } = this.props;
      const schedules = await this.scheduleService.list();
      const policy = await this.policyService.get(match.params.policy);
      this.setState({
        policy,
        schedules
      });
    } catch (ex) {
      console.error(ex);
    }
  }

  handleChange = name => event => {
    const { policy } = this.state;
    policy[name] = event.target.value;
    this.setState({ policy });
  };

  handleChangeTags = tags => {
    const { policy } = this.state;
    policy.tags = tags;
    this.setState({ policy });
  }

  handleChangeProjects = projects => {
    const { policy } = this.state;
    policy.projects = projects;
    this.setState({ policy });
  }

  handleSave = event => {
    try {
      const { history } = this.props;
      const { policy } = this.state;
      const response = this.policyService.add(policy);
      console.log(response);
      history.push('/policies/browser');

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
    const { policy, schedules } = this.state;

    if (policy) {
      return (
        <div className={classes.root}>

          <AppPageActions>
            <IconButton color="primary" aria-label="Back" onClick={this.handleRequestCancel}>
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="subheading" color="primary">
              Edit policy {policy.name}
            </Typography>
          </AppPageActions>


          <AppPageContent>
            <FormGroup row={false}>
              <TextField
                disabled
                id="policy-name"
                error={false}
                helperText=""
                label="Policy name"
                className={classes.textField}
                value={this.state.policy.name}
                onChange={this.handleChange('name')}
                margin="none"
                InputLabelProps={{
                  shrink: true
                }}
              />

              <FormControl className={classes.formControl}>
                <InputLabel shrink htmlFor="schedule-input">Schedule name</InputLabel>
                <Select
                  native
                  value={this.state.policy.schedulename}
                  onChange={this.handleChange('schedulename')}
                  inputProps={{
                    id: 'schedule-input',
                  }}
                >
                  <option value="" />
                  {
                    map(schedules, schedule => <option key={schedule} value={schedule}>{schedule}</option>)
                  }
                </Select>
              </FormControl>

              <PolicyProjects selected={policy.projects} onChange={this.handleChangeProjects} />

              <PolicyTags tags={policy.tags} onChange={this.handleChangeTags} />

            </FormGroup>

            <Button className={classes.button} variant="raised" color="primary" size="small" onClick={this.handleSave}>
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

PolicyEdit.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(PolicyEdit);
