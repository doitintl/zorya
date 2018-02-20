import React from 'react';
// import classNames from 'classnames';

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
// import PolicyProjects from '../../modules/components/PolicyProjects';
import PolicyTags from '../../modules/components/PolicyTags';
import AppPageContent from '../../modules/components/AppPageContent';
import AppPageActions from '../../modules/components/AppPageActions';
import PolicyService from '../../modules/api/policy';
import ScheduleService from '../../modules/api/schedule';
import { getDefaultPolicy } from '../../modules/utils/policy';

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

class PolicyCreate extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      policy: getDefaultPolicy()
    }

    this.policyService = new PolicyService();
    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    try {
      const schedules = await this.scheduleService.list();
      this.setState({
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

  // handleChangeProjects = projects => {
  //   const { policy } = this.state;
  //   policy.projects = projects;
  //   this.setState({ policy });
  // }

  handleChangeProjects = event => {
    const { policy } = this.state;
    policy.projects = event.target.value.replace(/\s/g,'').split(',');;
    this.setState({
      policy
    });
  }

  handleCreate = async event => {
    try {
      const { history } = this.props;
      const { policy } = this.state;
      const response = await this.policyService.add(policy);
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

    return (
      <div className={classes.root}>

        <AppPageActions>
          <IconButton color="primary" aria-label="Back" onClick={this.handleRequestCancel}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="subheading" color="primary">
            Create a policy
          </Typography>
        </AppPageActions>

        <AppPageContent>
          <FormGroup row={false}>
            <TextField
              id="policy-name"
              error={false}
              helperText=""
              label="Policy name"
              className={classes.textField}
              value={policy.name}
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
                value={policy.schedulename}
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

            <TextField
              id="projects-list"
              error={false}
              helperText="Separated by comma"
              label="Projects"
              className={classes.textField}
              value={policy.projects.join(',')}
              onChange={this.handleChangeProjects}
              margin="none"
              InputLabelProps={{
                shrink: true
              }}
            />

            {/* <PolicyProjects onChange={this.handleChangeProjects} /> */}

            <PolicyTags onChange={this.handleChangeTags} />

          </FormGroup>

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

export default withStyles(styles)(PolicyCreate);
