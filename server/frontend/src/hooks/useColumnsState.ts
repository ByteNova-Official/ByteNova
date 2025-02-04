import  { useState, useEffect } from 'react';

const useColumnsState = (initialState, localStorageKey) => {
  const [columnsStateMap, setColumnsStateMap] = useState();

  const localStorageState = localStorage[localStorageKey];
  console.log('localStorageState', localStorageState);

  useEffect(() => {
    if (localStorageState) {
      try {
        setColumnsStateMap(JSON.parse(localStorageState));
      } catch (e) {
        setColumnsStateMap(initialState);
        localStorage[localStorageKey] = '';
      }
    } else {
      setColumnsStateMap(initialState);
    }
  }, [])

  const setState = (value) => {
    console.log('value', value);
    localStorage[localStorageKey] = JSON.stringify(value);
    setColumnsStateMap(value);
  }

  return [
    columnsStateMap,
    setState,
  ]
}

export default useColumnsState;