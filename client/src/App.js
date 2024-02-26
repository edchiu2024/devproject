import { useState, useEffect, useCallback } from 'react'
import { BiCalendar } from "react-icons/bi"
import AddAppointment from "./components/AddAppointment"

function App() {


  let [appointmentList, setAppointmentList] = useState([]);


  //useCallBack -> only rendor once 
  //
  const fetchData = useCallback(() => {
    fetch('./data.json')
      .then(response => response.json())
      .then(data => {
        setAppointmentList(data)
      });
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData]);

  return (
    <div className="App container mx-auto mt-3 font-thin">
      <h1 className="text-5xl mb-3">
        <BiCalendar className="inline-block text-red-400 align-top" />Your Appointments</h1>
      <AddAppointment
        onSendAppointment={myAppointment => setAppointmentList([...appointmentList, myAppointment])}
        lastId={appointmentList.reduce((max, item) => Number(item.id) > max ? Number(item.id) : max, 0)}
      />
      
    </div>
  );
}

export default App;