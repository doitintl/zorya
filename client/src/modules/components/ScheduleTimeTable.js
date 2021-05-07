import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

// Material UI
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';

// Lodash
import map from 'lodash/map';
import find from 'lodash/find';
import flatten from 'lodash/flatten';

// react-lineto
import { Line } from 'react-lineto';

const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
const hours = [...Array(24).keys()];
const gutters = 4;
const boxSize = 36;

const getSelectionRect = (mouseDown, mouseUp) => {
  const selectionRect = {};
  if (mouseDown.x <= mouseUp.x) {
    selectionRect.left = mouseDown.x;
    selectionRect.right = mouseUp.x;
    if (mouseDown.y <= mouseUp.y) {
      selectionRect.top = mouseDown.y;
      selectionRect.bottom = mouseUp.y;
    } else {
      selectionRect.top = mouseUp.y;
      selectionRect.bottom = mouseDown.y;
    }
  } else {
    selectionRect.left = mouseUp.x;
    selectionRect.right = mouseDown.x;
    if (mouseDown.y <= mouseUp.y) {
      selectionRect.top = mouseDown.y;
      selectionRect.bottom = mouseUp.y;
    } else {
      selectionRect.top = mouseUp.y;
      selectionRect.bottom = mouseDown.y;
    }
  }
  return selectionRect;
};

const intersects = (rectA, rectB) => {
  return (
    rectA.left < rectB.right &&
    rectA.right > rectB.left &&
    rectA.top < rectB.bottom &&
    rectA.bottom > rectB.top
  );
};

const styles = (theme) => ({
  root: {
    margin: theme.spacing(2, 0),
  },
  row: {
    display: 'flex',
    flexDirection: 'row',
  },
  column: {
    display: 'flex',
    flexDirection: 'column',
  },
  hourBox: {
    height: boxSize,
    width: boxSize,
    margin: gutters,
  },
  columnButtonRoot: {
    minHeight: boxSize,
    minWidth: boxSize,
    margin: gutters,
    padding: 0,
  },
  rowButtonRoot: {
    minHeight: boxSize,
    minWidth: 48,
    margin: gutters,
    padding: 0,
  },
  boxContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  on: {
    backgroundColor: '#aed581',
  },
  off: {
    backgroundColor: '#eeeeee',
  },
  nextOn: {
    backgroundColor: '#7da453',
  },
  nextOff: {
    backgroundColor: '#bcbcbc',
  },
  crosshair: {
    cursor: 'crosshair',
  },
});

class ScheduleTimeTable extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      matrix: null,
      mouseDown: null,
      mouseCurrent: null,
    };
  }

  async componentDidMount() {
    try {
      const matrix = map(this.props.schedule.__ndarray__, (dayArray) =>
        map(dayArray, (hourValue) => ({ current: hourValue, next: null }))
      );
      this.setState({
        matrix,
      });
    } catch (ex) {
      console.error(ex);
    }
  }

  publishChanges = () => {
    const { matrix } = this.state;
    const ndarray = map(matrix, (day) => map(day, (hour) => hour.current));
    const schedule = {
      ...this.props.schedule,
      __ndarray__: ndarray,
    };
    this.props.onScheduleChange(schedule);
  };

  toggleDay = (dayIndex) => (event) => {
    this.setState(
      (prevState, props) => {
        const { matrix } = prevState;
        if (find(matrix[dayIndex], { current: 0 })) {
          matrix[dayIndex] = map(matrix[dayIndex], (hour) => ({
            current: 1,
            next: null,
          }));
        } else {
          matrix[dayIndex] = map(matrix[dayIndex], (hour) => ({
            current: 0,
            next: null,
          }));
        }
        return { matrix };
      },
      () => this.publishChanges()
    );
  };

  toggleHour = (hourIndex) => (event) => {
    this.setState(
      (prevState, props) => {
        const { matrix } = prevState;
        let hourIsOn = true;
        for (let i = 0; i < props.schedule.Shape[0]; i++) {
          hourIsOn = hourIsOn && !!matrix[i][hourIndex].current;
        }
        const newCurrent = hourIsOn ? 0 : 1;
        for (let i = 0; i < props.schedule.Shape[0]; i++) {
          matrix[i][hourIndex].current = newCurrent;
        }
        return { matrix };
      },
      () => this.publishChanges()
    );
  };

  toggleAll = (event) => {
    this.setState(
      (prevState, props) => {
        const matrix = prevState.matrix;
        const hasZero = find(flatten(matrix), { current: 0 });
        const newCurrent = hasZero ? 1 : 0;
        for (let dayIndex = 0; dayIndex < props.schedule.Shape[0]; dayIndex++) {
          for (
            let hourIndex = 0;
            hourIndex < props.schedule.Shape[1];
            hourIndex++
          ) {
            matrix[dayIndex][hourIndex].current = newCurrent;
          }
        }
        return {
          matrix,
        };
      },
      () => this.publishChanges()
    );
  };

  getDayGrid = (dayIndex, dayValues) => {
    const { classes } = this.props;

    const hourBlocks = map(dayValues, (hour, hourIndex) => (
      <div key={`day-${dayIndex}-hour-${hourIndex}`}>
        {hour.next !== null ? (
          <Paper
            className={classNames(classes.hourBox, {
              [classes.nextOn]: !!hour.next,
              [classes.nextOff]: !hour.next,
            })}
            elevation={2}
          />
        ) : (
          <Paper
            className={classNames(classes.hourBox, {
              [classes.on]: !!hour.current,
              [classes.off]: !hour.current,
            })}
            elevation={2}
          />
        )}
      </div>
    ));

    return hourBlocks;
  };

  handleMouseMove = (event) => {
    const { mouseDown, newCurrent } = this.state;
    const matrix = this.state.matrix.slice();
    const matrixRect = this.matrixDiv.getBoundingClientRect();

    const mouseCurrent = {
      x: event.clientX,
      y: event.clientY,
    };

    if (mouseCurrent.x < matrixRect.left) {
      mouseCurrent.x = matrixRect.left;
    }
    if (mouseCurrent.x > matrixRect.right) {
      mouseCurrent.x = matrixRect.right;
    }
    if (mouseCurrent.y < matrixRect.top) {
      mouseCurrent.y = matrixRect.top;
    }
    if (mouseCurrent.y > matrixRect.bottom) {
      mouseCurrent.y = matrixRect.bottom;
    }

    const selectionRect = getSelectionRect(mouseDown, mouseCurrent);

    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        const top =
          matrixRect.top +
          gutters +
          dayIndex * boxSize +
          dayIndex * gutters * 2;
        const left =
          matrixRect.left +
          gutters +
          hourIndex * boxSize +
          hourIndex * gutters * 2;
        const hourRect = {
          top,
          left,
          bottom: top + boxSize,
          right: left + boxSize,
        };
        if (intersects(hourRect, selectionRect)) {
          matrix[dayIndex][hourIndex].next = newCurrent;
        } else {
          matrix[dayIndex][hourIndex].next = null;
        }
      }
    }

    this.setState({
      matrix,
      mouseCurrent,
    });
  };

  handleMouseDown = (event) => {
    event.persist();
    if (event.button === 0) {
      const { matrix } = this.state;

      const mouseDown = {
        x: event.clientX,
        y: event.clientY,
      };

      const start = getSelectionRect(mouseDown, mouseDown);
      const matrixRect = this.matrixDiv.getBoundingClientRect();
      for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
        for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
          const top = matrixRect.top + dayIndex * (boxSize + gutters * 2);
          const left = matrixRect.left + hourIndex * (boxSize + gutters * 2);
          const hourRect = {
            top,
            left,
            bottom: top + boxSize + gutters * 2,
            right: left + boxSize + gutters * 2,
          };
          if (intersects(hourRect, start)) {
            const newCurrent = matrix[dayIndex][hourIndex].current ? 0 : 1;
            document.addEventListener('mousemove', this.handleMouseMove, false);
            document.addEventListener('mouseup', this.handleMouseUp, false);
            this.setState({
              mouseDown,
              newCurrent,
            });
          }
        }
      }
    }
  };

  handleMouseUp = (event) => {
    const { mouseDown } = this.state;
    document.removeEventListener('mouseup', this.handleMouseUp, false);
    document.removeEventListener('mousemove', this.handleMouseMove, false);
    if (mouseDown) {
      const mouseUp = {
        x: event.clientX,
        y: event.clientY,
      };

      const selectionRect = getSelectionRect(mouseDown, mouseUp);
      this.toggleSelectionBox(selectionRect);
    }

    this.setState({
      mouseDown: null,
      mouseCurrent: null,
    });
  };

  toggleSelectionBox = (selectionRect) => {
    const { newCurrent } = this.state;
    const matrix = this.state.matrix.slice();
    const matrixRect = this.matrixDiv.getBoundingClientRect();

    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        const top =
          matrixRect.top +
          gutters +
          dayIndex * boxSize +
          dayIndex * gutters * 2;
        const left =
          matrixRect.left +
          gutters +
          hourIndex * boxSize +
          hourIndex * gutters * 2;
        const hourRect = {
          top,
          left,
          bottom: top + boxSize,
          right: left + boxSize,
        };
        if (intersects(hourRect, selectionRect)) {
          matrix[dayIndex][hourIndex].current = newCurrent;
          matrix[dayIndex][hourIndex].next = null;
        }
      }
    }

    this.setState(
      {
        matrix,
      },
      () => this.publishChanges()
    );
  };

  render() {
    const { classes } = this.props;
    const { matrix, mouseDown, mouseCurrent } = this.state;

    return (
      matrix && (
        <div className={classes.root}>
          <div className={classes.row}>
            <Button
              disableRipple
              disableFocusRipple
              classes={{ root: classes.rowButtonRoot }}
              onClick={this.toggleAll}
            >
              ALL
            </Button>
            {map(hours, (hour) => (
              <div key={`hour-${hour}`}>
                <Button
                  disableRipple
                  disableFocusRipple
                  variant="contained"
                  classes={{ root: classes.columnButtonRoot }}
                  onClick={this.toggleHour(hour)}
                >
                  {hour < 10 ? `0${hour}` : hour}
                </Button>
              </div>
            ))}
          </div>

          <div className={classes.row}>
            <div className={classes.column}>
              {map(days, (day, dayIndex) => (
                <Button
                  key={`day-${dayIndex}`}
                  disableRipple
                  disableFocusRipple
                  variant="contained"
                  classes={{ root: classes.rowButtonRoot }}
                  onClick={this.toggleDay(dayIndex)}
                >
                  {day}
                </Button>
              ))}
            </div>

            <div
              className={classNames(classes.column, classes.crosshair)}
              ref={(matrixDiv) => (this.matrixDiv = matrixDiv)}
              onMouseDown={this.handleMouseDown}
            >
              {mouseDown && mouseCurrent && (
                <div>
                  <Line
                    border="1px dashed #fff"
                    x0={mouseDown.x}
                    y0={mouseDown.y}
                    x1={mouseCurrent.x}
                    y1={mouseDown.y}
                  />
                  <Line
                    border="1px dashed #fff"
                    x0={mouseCurrent.x}
                    y0={mouseDown.y}
                    x1={mouseCurrent.x}
                    y1={mouseCurrent.y}
                  />
                  <Line
                    border="1px dashed #fff"
                    x0={mouseCurrent.x}
                    y0={mouseCurrent.y}
                    x1={mouseDown.x}
                    y1={mouseCurrent.y}
                  />
                  <Line
                    border="1px dashed #fff"
                    x0={mouseDown.x}
                    y0={mouseCurrent.y}
                    x1={mouseDown.x}
                    y1={mouseDown.y}
                  />
                </div>
              )}

              {map(matrix, (dayValues, dayIndex) => (
                <div key={`day-${dayIndex}`} className={classes.row}>
                  {this.getDayGrid(dayIndex, dayValues)}
                </div>
              ))}
            </div>
          </div>
        </div>
      )
    );
  }
}

ScheduleTimeTable.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(ScheduleTimeTable);
