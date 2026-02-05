import { render, screen } from '@testing-library/react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../card'

describe('Card', () => {
  it('should render card with content', () => {
    render(
      <Card>
        <CardContent>Test content</CardContent>
      </Card>
    )
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('should render complete card structure', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
          <CardDescription>Test Description</CardDescription>
        </CardHeader>
        <CardContent>Test content</CardContent>
        <CardFooter>Test footer</CardFooter>
      </Card>
    )

    expect(screen.getByText('Test Title')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
    expect(screen.getByText('Test content')).toBeInTheDocument()
    expect(screen.getByText('Test footer')).toBeInTheDocument()
  })

  it('should apply custom className to Card', () => {
    const { container } = render(
      <Card className="custom-card">
        <CardContent>Content</CardContent>
      </Card>
    )
    const card = container.firstChild
    expect(card).toHaveClass('custom-card')
  })

  it('should apply custom className to CardHeader', () => {
    const { container } = render(
      <Card>
        <CardHeader className="custom-header">
          <CardTitle>Title</CardTitle>
        </CardHeader>
      </Card>
    )
    expect(container.querySelector('.custom-header')).toBeInTheDocument()
  })

  it('should apply custom className to CardTitle', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle className="custom-title">Title</CardTitle>
        </CardHeader>
      </Card>
    )
    const title = screen.getByText('Title')
    expect(title).toHaveClass('custom-title')
  })

  it('should apply custom className to CardDescription', () => {
    render(
      <Card>
        <CardHeader>
          <CardDescription className="custom-description">Description</CardDescription>
        </CardHeader>
      </Card>
    )
    const description = screen.getByText('Description')
    expect(description).toHaveClass('custom-description')
  })

  it('should apply custom className to CardContent', () => {
    const { container } = render(
      <Card>
        <CardContent className="custom-content">Content</CardContent>
      </Card>
    )
    expect(container.querySelector('.custom-content')).toBeInTheDocument()
  })

  it('should apply custom className to CardFooter', () => {
    const { container } = render(
      <Card>
        <CardFooter className="custom-footer">Footer</CardFooter>
      </Card>
    )
    expect(container.querySelector('.custom-footer')).toBeInTheDocument()
  })

  it('should forward ref to Card', () => {
    const ref = jest.fn()
    render(
      <Card ref={ref}>
        <CardContent>Content</CardContent>
      </Card>
    )
    expect(ref).toHaveBeenCalledWith(expect.any(HTMLDivElement))
  })

  it('should forward ref to CardHeader', () => {
    const ref = jest.fn()
    render(
      <Card>
        <CardHeader ref={ref}>
          <CardTitle>Title</CardTitle>
        </CardHeader>
      </Card>
    )
    expect(ref).toHaveBeenCalledWith(expect.any(HTMLDivElement))
  })

  it('should render multiple cards independently', () => {
    render(
      <>
        <Card>
          <CardContent>Card 1</CardContent>
        </Card>
        <Card>
          <CardContent>Card 2</CardContent>
        </Card>
      </>
    )

    expect(screen.getByText('Card 1')).toBeInTheDocument()
    expect(screen.getByText('Card 2')).toBeInTheDocument()
  })
})
