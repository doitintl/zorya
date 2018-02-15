class ScheduleService {
  list = async () => {
    const response = await fetch(`/api/v1/list_schedules`, {
      method: 'GET'
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response.json();
  }

  get = async schedule => {
    const response = await fetch(`/api/v1/get_schedule?schedule=${schedule}`, {
      method: 'GET'
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response.json();
  }

  add = async (schedule) => {
    const body = {
      ...schedule
    }

    const response = await fetch(`/api/v1/add_schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response.json();
  }

}

export default ScheduleService;