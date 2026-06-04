import '@testing-library/jest-dom'; // <-- This fixes the "toBeInTheDocument is not a function" error
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders project heading', () => {
  render(<App />);
  expect(screen.getByText(/Project 04/i)).toBeInTheDocument();
});

test('counter starts at 0', () => {
  render(<App />);
  expect(screen.getByText(/Clicked 0 times/i)).toBeInTheDocument();
});

test('counter increments on click', () => {
  render(<App />);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText(/Clicked 1 time/i)).toBeInTheDocument();
});

test('shows deployment info section', () => {
  render(<App />);
  expect(screen.getByText(/Deployment Info/i)).toBeInTheDocument();
});