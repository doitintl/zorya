class PolicyService {
  list = async () => {
    const response = await fetch(`/api/v1/list_policies?verbose=true`, {
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

  get = async (policy) => {
    const response = await fetch(`/api/v1/get_policy?policy=${policy}`, {
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

  delete = async (policy) => {
    const response = await fetch(`/api/v1/del_policy?policy=${policy}`, {
      method: 'GET',
      credentials: 'same-origin',
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response;
  };

  add = async (policy) => {
    const response = await fetch(`/api/v1/add_policy`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(policy),
    });

    if (!response.ok) {
      console.error(response);
      const responseBody = await response.text();
      throw Error(responseBody || response.statusText);
    }

    return response;
  };
}

export default PolicyService;
