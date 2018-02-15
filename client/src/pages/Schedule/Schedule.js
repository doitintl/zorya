import React from 'react';
import classNames from 'classnames';

// Material UI
import { withStyles } from 'material-ui/styles';
import Typography from 'material-ui/Typography';
// import Divider from 'material-ui/Divider';
import Paper from 'material-ui/Paper';
import Button from 'material-ui/Button';

// Lodash
import map from 'lodash/map';
import times from 'lodash/times';
import includes from 'lodash/includes';
import constant from 'lodash/constant';

// Project
import ScheduleService from '../../modules/api/schedule';

const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const hours = [...Array(24).keys()];

const styles = theme => ({
  root: {
    padding: theme.spacing.unit,
  },
  row: {
    display: 'flex',
    flexDirection: 'row'
  },
  boxSize: {
    height: '36px',
    width: '36px',
    margin: theme.spacing.unit / 4,
  },
  hourButtonRoot: {
    minHeight: '36px',
    minWidth: '36px',
  },
  longBoxSize: {
    height: '36px',
    width: '100px',
    margin: theme.spacing.unit / 4,
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
  clickable: {
    cursor: 'pointer'
  }
});

class Schedule extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      schedule: null,
      matrix: null,
    }

    this.scheduleService = new ScheduleService();
  }

  async componentDidMount() {
    const { match } = this.props;
    const schedule = await this.scheduleService.get(match.params.schedule);
    console.log(schedule.__ndarray__);
    this.setState({
      schedule,
      matrix: schedule.__ndarray__.slice()
    });
  }

  getDayGrid = (dayIndex, dayValues) => {
    const { classes } = this.props;

    const hourBlocks = map(dayValues, (value, index) => (
      <div key={`day-${dayIndex}-hour-${index}`}>
        {
          value ?
            (
              <Paper className={classNames(classes.boxSize, classes.on)} elevation={2} />
            ) : (
              <Paper className={classNames(classes.boxSize, classes.off)} elevation={2} />
            )
        }
      </div>
    ))

    return [
      <div key={`day-${dayIndex}`}>
        <div className={classNames(classes.longBoxSize, classes.boxContent, classes.clickable)}>
          {/* <Typography variant="caption" color="textSecondary" onClick={this.toggleDay(dayIndex)}>
            {days[dayIndex]}
          </Typography> */}
          <Button disableRipple disableFocusRipple variant="raised" className={classNames(classes.longBoxSize)} onClick={this.toggleDay(dayIndex)}>
            {days[dayIndex]}
          </Button>
        </div>
      </div>,
      ...hourBlocks
    ]
  }

  toggleDay = dayIndex => event => {
    this.setState((prevState, props) => {
      const { matrix } = prevState;
      if (includes(matrix[dayIndex], 0)) {
        matrix[dayIndex] = times(24, constant(1));
      } else {
        matrix[dayIndex] = times(24, constant(0));
      }
      return { matrix };
    })
  }

  toggleHour = hourIndex => event => {
    this.setState((prevState, props) => {
      const { schedule, matrix } = prevState;
      const hourHasZero = !(matrix[0][hourIndex] && matrix[1][hourIndex] && matrix[2][hourIndex] && matrix[3][hourIndex] && matrix[4][hourIndex] && matrix[5][hourIndex] && matrix[6][hourIndex]);
      const nextVal = hourHasZero ? 1 : 0;
      for (let i = 0; i < schedule.Shape[0]; i++) {
        matrix[i][hourIndex] = nextVal;
      }
      return { matrix };
    })
  }

  render() {
    const { classes } = this.props;
    const { schedule, matrix } = this.state;

    return (
      schedule &&
      <div className={classes.root}>
        <Typography variant="body2" color="textSecondary">
          Name: {schedule.name}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Timezone: {schedule.timezone}
        </Typography>

        <div>
          <div className={classes.row}>
            <div className={classNames(classes.longBoxSize, classes.boxContent)}>
              <Typography variant="button" color="textSecondary">
                Day \ Hour
              </Typography>
            </div>
            {
              map(hours, hour =>
                <div key={`hour-${hour}`}>
                  <div className={classNames(classes.boxSize, classes.boxContent)}>
                    <Button disableRipple disableFocusRipple variant="raised" classes={{ root: classes.hourButtonRoot }}  onClick={this.toggleHour(hour)}>
                      {
                        hour < 10 ? `0${hour}` : hour
                      }
                    </Button>
                  </div>
                </div>)
            }
          </div>

          {
            map(matrix, (dayValues, dayIndex) =>
              <div key={`${dayIndex}`} className={classes.row}>
                {this.getDayGrid(dayIndex, dayValues)}
              </div>)
          }
        </div>


      </div>

    )
  }
}

export default withStyles(styles)(Schedule);
