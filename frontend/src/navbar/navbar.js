import React, { Component } from "react";

import {
    Menu,
    Row,
    Col
} from 'antd';
import styles from "./navbar.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap'


// class NavBar extends Component {
const NavBar = () => {
    return (
        <Navbar collapseOnSelect expand="lg" className="navbar-header navbar-light">
          <Navbar.Brand href="#/"><img
                    className="logo"
                    src="https://identity.usc.edu/files/2011/12/combo_gold_white_cardinal.png"
                    alt="USC"
                /></Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="mr-auto">
              <Nav.Link className="navbar-link" href="#/">Home</Nav.Link>
              <Nav.Link className="navbar-link" href="#evaluation">Evaluation</Nav.Link>
              <Nav.Link className="navbar-link" href="#submit">Submit</Nav.Link>
              <Nav.Link className="navbar-link-highlight" href="https://github.com/scc-usc/covid19-forecast-bench" target="_blank">Github</Nav.Link>
            </Nav>
            <Nav>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
    )
}
export default NavBar;