import * as React from 'react';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';
import {red} from '@mui/material/colors';


function UserCard({user}) {
    return (
        <div>
            <Card sx={{maxWidth: 345, m:1}}>
                <CardHeader
                    avatar={
                        <Avatar sx={{bgcolor: red[500]}} aria-label="recipe">
                            {user.name[0]}
                        </Avatar>
                    }
                    title={user.name}
                    subheader={user.location}
                />

                <CardContent>
                    <Typography variant="body2" sx={{color: 'text.secondary'}}>
                        Twój znajomy {user.name} opublikował {user.posts} postów.
                    </Typography>
                </CardContent>


            </Card>
        </div>
    );
}

export default UserCard;
