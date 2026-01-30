import React from 'react';
import {Link} from "react-router-dom";
import {Button} from "@mui/material";

function Services(props) {
    return (
        <div>
            <h1 className="services__title"> Services </h1>
            <Button sx={{m:1}}
                className="services__button"
                variant='contained'
                size='large'
                component={Link}
                to='/map'
            >
                Przejdź do Mapy
            </Button>


            <Button sx={{m:1}}
            className="services__button"
            variant='contained'
            size='large'
            component={Link}
            to='/newuser'
            >
                Dodaj nowego użytkownika
            </Button>

            <Button sx={{m:1}}
            className="services__button"
            variant='contained'
            size='large'
            component={Link}
            to='/listofitems'
            >
                Lista użytkowników
            </Button>

        </div>
    );
}
export default Services;