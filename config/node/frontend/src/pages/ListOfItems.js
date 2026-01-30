import React, {useEffect, useState} from 'react';
import UserCard from "../components/UserCard";
import {Paper} from "@mui/material";

function ListOfItems(props) {
    console.log("List Of Items")

    const [users, setUsers] = useState([]);

    useEffect(() => {
        console.log("using an Effect...")
        fetch('http://localhost:10000/app/get_users')
        // fetch('https://jsonplaceholder.typicode.com/users')
            .then(res => res.json())
            .then(res => {
                console.log(res);
                setUsers(res);
            })
    },
        []
    )
console.log("To jest users:", users);
    return (
        <div>
            <h1 className="listofitems__title"> List Of Items </h1>
            <Paper elevation={3} sx={{p:4}}>

                <div style={{ display: 'flex', flexWrap: 'wrap', flexDirection: 'column' }}>
                     {users?.users?.map(user =>
                         <UserCard id={user.id} user={user}/>)}
                </div>
            </Paper>
        </div>
    );
}

export default ListOfItems;