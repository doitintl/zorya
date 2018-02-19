class PolicyService {
  list = async () => {
    const response = await fetch(`/api/v1/list_policies`, {
      method: 'GET'
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response.json();
  }

  get = async policy => {
    const response = await fetch(`/api/v1/get_policy?policy=${policy}`, {
      method: 'GET'
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response.json();
  }

  add = async policy => {
    const response = await fetch(`/api/v1/add_policy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(policy)
    });

    if (!response.ok) {
      console.error(response);
      throw Error(response.statusText);
    }

    return response;
  }
}

export default PolicyService;