import React from 'react';
import {Typography, Button} from '@mui/material';
import {Link} from "react-router-dom";

function Home(props) {
    return (
        <div ClassName="home">
            <h1 className="home__title">GEOPORTAL</h1>
            <Typography classname='home__subtitle'>
                Geoportal tematyczny poświęcony danym przestrzennym przetwarzanym
            </Typography>

            <Button
                className="home__button"
                variant='contained'
                size='large'
                component={Link}
                to='services'
            >
                START
            </Button>

        </div>
    );
}

export default Home;