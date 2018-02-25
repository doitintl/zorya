import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from 'material-ui/styles';
import Input, { InputLabel } from 'material-ui/Input';
import { MenuItem } from 'material-ui/Menu';
import { FormControl } from 'material-ui/Form';
import { ListItemText } from 'material-ui/List';
import Select from 'material-ui/Select';
import Checkbox from 'material-ui/Checkbox';
import Tooltip from 'material-ui/Tooltip';

const styles = theme => ({
  root: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  formControl: {
    marginBottom: theme.spacing.unit * 3,
    minWidth: 250,
    maxWidth: 250,
  },
});

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const projects = [
  "project-a",
  "project-b",
  "project-c",
  "project-d",
  "project-e",
  "project-f",
];

class PolicyProjects extends React.Component {
  state = {
    selected: [],
  };

  componentDidMount() {
    const { selected } = this.props;
    if (selected) {
      this.setState({
        selected
      })
    }
  }

  handleChange = event => {
    this.setState({ selected: event.target.value }, () => this.props.onChange(this.state.selected));
  };

  render() {
    const { classes } = this.props;
    const { selected } = this.state;

    return (
      <div className={classes.root}>
        <Tooltip
          title={selected.length > 3 ? selected.join(', ') : ''}
          placement="right"
          enterDelay={300}
        >
          <FormControl className={classes.formControl}>
            <InputLabel htmlFor="policy-projects" shrink>Projects</InputLabel>
            <Select
              multiple
              value={selected}
              onChange={this.handleChange}
              input={<Input id="policy-projects" />}
              renderValue={selected => selected.join(', ')}
              MenuProps={MenuProps}
            >
              {projects.map(project => (
                <MenuItem key={project} value={project} disableGutters>
                  <Checkbox checked={selected.indexOf(project) > -1} />
                  <ListItemText primary={project} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Tooltip>
      </div>
    );
  }
}

PolicyProjects.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(PolicyProjects);