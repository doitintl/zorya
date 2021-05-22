class ScheduleService {
  list = async () => {
    const response = await fetch(`/api/v1/list_schedules?verbose=true`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response.json();
  };

  get = async (schedule) => {
    const response = await fetch(`/api/v1/get_schedule?schedule=${schedule}`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response.json();
  };

  delete = async (schedule) => {
    const response = await fetch(`/api/v1/del_schedule?schedule=${schedule}`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response;
  };

  add = async (schedule) => {
    const response = await fetch(`/api/v1/add_schedule`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(schedule),
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response;
  };

  timezones = async () => {
    const response = await fetch(`/api/v1/time_zones`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response.json();
  };
}

export default ScheduleService;
