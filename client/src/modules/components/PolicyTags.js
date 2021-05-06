import React from 'react';
import PropTypes from 'prop-types';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import FormGroup from '@material-ui/core/FormGroup';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import ClearIcon from '@material-ui/icons/Clear';

// Lodash
import map from 'lodash/map';
import forOwn from 'lodash/forOwn';

const TEXT_FIELD_WIDTH = 250;

const styles = (theme) => ({
  root: {
    marginBottom: theme.spacing(3),
  },
  textField: {
    width: TEXT_FIELD_WIDTH,
    marginRight: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  iconButton: {
    width: 32,
    height: 32,
  },
  addButton: {
    width: TEXT_FIELD_WIDTH * 2 + theme.spacing(1),
  },
  sizeSmallButton: {
    padding: 0,
    minHeight: 24,
  },
});

class PolicyTags extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      tags: [
        {
          key: '',
          value: '',
        },
      ],
    };
  }

  componentDidMount() {
    if (this.props.tags && this.props.tags.length > 0) {
      let tags = [];
      this.props.tags.forEach((tag) => {
        forOwn(tag, (value, key) => {
          tags.push({
            key,
            value,
          });
        });
      });
      this.setState({
        tags,
      });
    }
  }

  publishChanges = (shouldUpdateErrors) => {
    const tags = map(this.state.tags, (tag) => ({
      [tag.key]: tag.value,
    }));
    this.props.onChange(tags, shouldUpdateErrors);
  };

  handleChange = (index, name) => (event) => {
    const tags = this.state.tags.slice();
    tags[index][name] = event.target.value;
    this.setState({ tags }, () => this.publishChanges(false));
  };

  handleClearTag = (index) => (event) => {
    const tags = this.state.tags.slice();
    if (tags.length > 1) {
      tags.splice(index, 1);
      this.setState({ tags }, () => this.publishChanges(true));
    }
  };

  handleAddTag = (event) => {
    const tags = this.state.tags.slice();
    tags.push({
      key: '',
      value: '',
    });
    this.setState({ tags }, () => this.publishChanges(false));
  };

  render() {
    const { classes, error } = this.props;
    const { tags } = this.state;

    return (
      <div className={classes.root}>
        {map(tags, (tag, index) => (
          <FormGroup row key={index}>
            <TextField
              id="policy-tag-value"
              error={error[index] && error[index][0]}
              helperText=""
              placeholder="Key"
              className={classes.textField}
              value={tags[index].key}
              onChange={this.handleChange(index, 'key')}
              margin="none"
            />
            <TextField
              id="policy-tag-key"
              error={error[index] && error[index][1]}
              helperText=""
              placeholder="Value"
              className={classes.textField}
              value={tags[index].value}
              onChange={this.handleChange(index, 'value')}
              margin="none"
            />

            {tags.length > 1 && (
              <IconButton
                className={classes.iconButton}
                aria-label="Clear"
                onClick={this.handleClearTag(index)}
                classes={{
                  root: classes.iconButton,
                }}
              >
                <ClearIcon />
              </IconButton>
            )}
          </FormGroup>
        ))}

        {tags.length < 7 && (
          <Button
            variant="outlined"
            color="primary"
            size="small"
            className={classes.addButton}
            onClick={this.handleAddTag}
            classes={{
              sizeSmall: classes.sizeSmallButton,
            }}
          >
            Add tag
          </Button>
        )}
      </div>
    );
  }
}
PolicyTags.propTypes = {
  classes: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.array.isRequired,
};

export default withStyles(styles)(PolicyTags);
