import React from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import Downshift from 'downshift';

function renderInput(inputProps) {
  const { InputProps, classes, ref, ...other } = inputProps;

  return (
    <TextField
      margin="none"
      {...other}
      inputRef={ref}
      InputProps={{
        classes: {
          input: classes.input,
        },
        ...InputProps,
      }}
    />
  );
}

function renderSuggestion(params) {
  const { suggestion, index, itemProps, highlightedIndex, selectedItem } =
    params;
  const isHighlighted = highlightedIndex === index;
  const isSelected = selectedItem === suggestion;

  return (
    <MenuItem
      {...itemProps}
      key={suggestion}
      selected={isHighlighted}
      component="div"
      style={{
        fontWeight: isSelected ? 500 : 400,
      }}
    >
      {suggestion}
    </MenuItem>
  );
}

const styles = (theme) => ({
  container: {
    width: 250,
    marginBottom: theme.spacing(3),
  },
  suggestionsContainer: {
    position: 'absolute',
    maxHeight: 200,
    width: 250,
    overflow: 'auto',
    zIndex: 1000,
  },
});

class ScheduleTimezone extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {};
  }

  getSuggestions = (inputValue) =>
    this.props.timezones
      .filter(
        (suggestion) =>
          !inputValue ||
          suggestion.toLowerCase().includes(inputValue.toLowerCase())
      )
      .slice(0, 20);

  render() {
    const { classes, onSelect, selected } = this.props;

    return (
      <Downshift onSelect={onSelect} selectedItem={selected || null}>
        {({
          getInputProps,
          getItemProps,
          isOpen,
          inputValue,
          selectedItem,
          highlightedIndex,
        }) => (
          <div className={classes.container}>
            {renderInput({
              fullWidth: true,
              classes,
              InputProps: getInputProps({
                placeholder: 'Search timezone',
                id: 'timezone',
              }),
            })}
            {isOpen ? (
              <Paper
                square
                elevation={2}
                className={classes.suggestionsContainer}
              >
                {this.getSuggestions(inputValue).map((suggestion, index) =>
                  renderSuggestion({
                    suggestion,
                    index,
                    itemProps: getItemProps({ item: suggestion }),
                    highlightedIndex,
                    selectedItem,
                  })
                )}
              </Paper>
            ) : null}
          </div>
        )}
      </Downshift>
    );
  }
}

ScheduleTimezone.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(ScheduleTimezone);
