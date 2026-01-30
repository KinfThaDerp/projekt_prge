import {createHashRouter} from "react-router";
import {Home, About, Map, Services, ListOfItems, NewUser} from "./LazyImports";

const routes = createHashRouter(
    [
        {
            path: '/',
            element: <Home/>,
        },
        {
            path: '/about',
            element: <About/>,
        },
        {
            path: '/listofitems',
            element: <ListOfItems/>,
        },
        {
            path: '/newuser',
            element: <NewUser/>,
        },
        {
            path: '/map',
            element: <Map/>,
        },
        {
            path: '/services',
            element: <Services/>,
        },
        {
            path: "*",
            element: <div>404</div>
        },

    ]
)

export default routes;