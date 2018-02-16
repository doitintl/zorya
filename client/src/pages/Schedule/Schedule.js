import React from 'react';
import classNames from 'classnames';

// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
import Paper from 'material-ui/Paper';
import Button from 'material-ui/Button';

// Lodash
import map from 'lodash/map';
import find from 'lodash/find';
import flatten from 'lodash/flatten';

import { Line } from 'react-lineto';

// Project
import ScheduleService from '../../modules/api/schedule';

const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const hours = [...Array(24).keys()];
const gutters = 4;
const boxSize = 36;

const styles = theme => ({
  root: {
    padding: theme.spacing.unit,
  },
  row: {
    display: 'flex',
    flexDirection: 'row'
  },
  column: {
    display: 'flex',
    flexDirection: 'column'
  },
  boxSize: {
    height: boxSize,
    width: boxSize,
    margin: gutters,
    cursor: 'pointer'
  },
  hourButtonRoot: {
    minHeight: boxSize,
    minWidth: boxSize,
  },
  longBoxSize: {
    height: boxSize,
    width: 100,
    margin: gutters,
    cursor: 'pointer'
  },
  boxContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  on: {
    backgroundColor: theme.palette.primary.dark,
  },
  off: {
    backgroundColor: theme.palette.secondary.dark,
  },
  nextOn: {
    backgroundColor: theme.palette.primary.main,
  },
  nextOff: {
    backgroundColor: theme.palette.secondary.main,
  },
  line: {
    borderStyle: 'dashed',
    borderWidth: '1px',
    borderColor: 'white',
  }
});

class Schedule extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: null,
      matrix: null,

      mouseDown: null,
      mouseCurrent: null
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    try {
      const schedule = await this.scheduleService.get(match.params.schedule);
      const matrix = map(schedule.__ndarray__.slice(), dayArray =>
        map(dayArray, hourValue => ({ original: hourValue, current: hourValue, next: null }))
      )
      this.setState({
        schedule,
        matrix
      });
    } catch (ex) {
      console.error(ex);
    }

  }

  toggleDay = dayIndex => event => {
    this.setState((prevState, props) => {
      const { matrix } = prevState;
      if (find(matrix[dayIndex], { current: 0 })) {
        matrix[dayIndex] = map(matrix[dayIndex], hour => ({ original: hour.original, current: 1, next: null }));
      } else {
        matrix[dayIndex] = map(matrix[dayIndex], hour => ({ original: hour.original, current: 0, next: null }));
      }
      return { matrix };
    })
  }

  toggleHour = hourIndex => event => {
    this.setState((prevState, props) => {
      const { schedule, matrix } = prevState;
      let hourIsOn = true;
      for (let i = 0; i < schedule.Shape[0]; i++) {
        hourIsOn = hourIsOn && !!matrix[i][hourIndex].current;
      }
      const newCurrent = hourIsOn ? 0 : 1;
      for (let i = 0; i < schedule.Shape[0]; i++) {
        matrix[i][hourIndex].current = newCurrent;
      }
      return { matrix };
    })
  }

  toggleAll = event => {
    const matrix = this.state.matrix.slice();
    const hasZero = find(flatten(matrix), { current: 0 });
    const newCurrent = hasZero ? 1 : 0;
    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        matrix[dayIndex][hourIndex].current = newCurrent;
      }
    }
    this.setState({
      matrix
    })
  }

  getDayGrid = (dayIndex, dayValues) => {
    const { classes } = this.props;

    const hourBlocks = map(dayValues, (hour, hourIndex) => (
      <div key={`day-${dayIndex}-hour-${hourIndex}`} >
        {
          hour.next !== null ?
            (
              <Paper className={classNames(classes.boxSize, { [classes.nextOn]: !!hour.next, [classes.nextOff]: !hour.next })} elevation={2} />
            ) : (
              <Paper className={classNames(classes.boxSize, { [classes.on]: !!hour.current, [classes.off]: !hour.current })} elevation={2} />
            )
        }
      </div>
    ))

    return hourBlocks;
  }

  handleMouseMove = event => {
    const { mouseDown, newCurrent } = this.state;
    const matrix = this.state.matrix.slice();

    const mouseCurrent = {
      x: event.clientX,
      y: event.clientY
    };

    const matrixRect = this.matrixDiv.getBoundingClientRect();
    const selectionRect = getSelectionRect(mouseDown, mouseCurrent);

    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        const top = matrixRect.top + gutters + dayIndex * boxSize + dayIndex * gutters * 2;
        const left = matrixRect.left + gutters + hourIndex * boxSize + hourIndex * gutters * 2;
        const hourRect = {
          top,
          left,
          bottom: top + boxSize,
          right: left + boxSize
        }
        if (intersects(hourRect, selectionRect)) {
          matrix[dayIndex][hourIndex].next = newCurrent;
        } else {
          matrix[dayIndex][hourIndex].next = null;
        }
      }
    }

    this.setState({
      matrix,
      mouseCurrent
    })
  }

  handleMouseDown = event => {
    event.persist();
    const { matrix } = this.state;

    const mouseDown = {
      x: event.clientX,
      y: event.clientY
    };

    const start = getSelectionRect(mouseDown, mouseDown);
    const matrixRect = this.matrixDiv.getBoundingClientRect();
    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        const top = matrixRect.top + gutters + dayIndex * boxSize + dayIndex * gutters * 2;
        const left = matrixRect.left + gutters + hourIndex * boxSize + hourIndex * gutters * 2;
        const hourRect = {
          top,
          left,
          bottom: top + boxSize,
          right: left + boxSize
        }
        if (intersects(hourRect, start)) {
          const newCurrent = matrix[dayIndex][hourIndex].current ? 0 : 1;
          document.addEventListener('mousemove', this.handleMouseMove, false);
          this.setState({
            mouseDown,
            newCurrent
          });
        }
      }
    }
  }

  handleMouseUp = event => {
    const { mouseDown } = this.state;
    document.removeEventListener('mousemove', this.handleMouseMove, false);
    if (mouseDown) {
      event.persist();

      const mouseUp = {
        x: event.clientX,
        y: event.clientY
      }

      const selectionRect = getSelectionRect(mouseDown, mouseUp);
      this.toggleSelectionBox(selectionRect);
    }

    this.setState({
      mouseDown: null,
      mouseCurrent: null
    })
  }

  toggleSelectionBox = (selectionRect) => {
    const { newCurrent } = this.state;
    const matrix = this.state.matrix.slice();
    const matrixRect = this.matrixDiv.getBoundingClientRect();

    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      for (let hourIndex = 0; hourIndex < 24; hourIndex++) {
        const top = matrixRect.top + gutters + dayIndex * boxSize + dayIndex * gutters * 2;
        const left = matrixRect.left + gutters + hourIndex * boxSize + hourIndex * gutters * 2;
        const hourRect = {
          top,
          left,
          bottom: top + boxSize,
          right: left + boxSize
        }
        if (intersects(hourRect, selectionRect)) {
          matrix[dayIndex][hourIndex].current = newCurrent;
          matrix[dayIndex][hourIndex].next = null;
        }
      }
    }

    this.setState({
      matrix
    })

  }

  render() {
    const { classes } = this.props;
    const { schedule, matrix, mouseDown, mouseCurrent } = this.state;

    return (
      schedule &&
      <div className={classes.root}>
        <Typography variant="body2" color="textSecondary">
          Name: {schedule.name}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Timezone: {schedule.timezone}
        </Typography>

        <div className={classes.row}>
          <div className={classNames(classes.longBoxSize, classes.boxContent)} onClick={this.toggleAll}>
            <Typography variant="button" color="textSecondary">
              ALL
              </Typography>
          </div>
          {
            map(hours, hour =>
              <div key={`hour-${hour}`}>
                <div className={classNames(classes.boxSize, classes.boxContent)}>
                  <Button disableRipple disableFocusRipple variant="raised" classes={{ root: classes.hourButtonRoot }} onClick={this.toggleHour(hour)}>
                    {
                      hour < 10 ? `0${hour}` : hour
                    }
                  </Button>
                </div>
              </div>)
          }
        </div>

        <div className={classes.row}>
          <div className={classes.column}>
            {
              map(days, (day, dayIndex) =>
                <div key={`day-${dayIndex}`} className={classNames(classes.longBoxSize, classes.boxContent)}>
                  <Button disableRipple disableFocusRipple variant="raised" className={classNames(classes.longBoxSize)} onClick={this.toggleDay(dayIndex)}>
                    {day}
                  </Button>
                </div>)
            }
          </div>
          <div
            className={classes.column}
            ref={matrixDiv => this.matrixDiv = matrixDiv}
            onMouseDown={this.handleMouseDown}
            onMouseUp={this.handleMouseUp}
          >
            {

              mouseDown && mouseCurrent &&
              // <div className={classes.selectionBox} style={{ position: 'absolute', top: `${mouseDown.y}`, left: `${mouseDown.x}`}}>
              // </div>
              <div>
                <Line className={classes.line} x0={mouseDown.x} y0={mouseDown.y} x1={mouseCurrent.x} y1={mouseDown.y} />
                <Line className={classes.line} x0={mouseCurrent.x} y0={mouseDown.y} x1={mouseCurrent.x} y1={mouseCurrent.y} />
                <Line className={classes.line} x0={mouseCurrent.x} y0={mouseCurrent.y} x1={mouseDown.x} y1={mouseCurrent.y} />
                <Line className={classes.line} x0={mouseDown.x} y0={mouseCurrent.y} x1={mouseDown.x} y1={mouseDown.y} />
              </div>
            }

            {
              map(matrix, (dayValues, dayIndex) =>
                <div key={`day-${dayIndex}`} className={classes.row}>
                  {this.getDayGrid(dayIndex, dayValues)}
                </div>)
            }
          </div>

        </div>
      </div>

    )
  }
}

export default withStyles(styles)(Schedule);

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
}


const intersects = (rectA, rectB) => {
  return (rectA.left < rectB.right && rectA.right > rectB.left &&
    rectA.top < rectB.bottom && rectA.bottom > rectB.top)
}