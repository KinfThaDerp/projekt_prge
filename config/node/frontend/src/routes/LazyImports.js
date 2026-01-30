import {lazy} from 'react';

export const Home = lazy( () => import('../pages/Home'))
export const About = lazy( () => import('../pages/About'))
export const ListOfItems = lazy( () => import('../pages/ListOfItems'))
export const NewUser = lazy (() => import('../pages/NewUser'))
export const Map = lazy( () => import('../pages/Map'))
export const Services = lazy( () => import('../pages/Services'))
