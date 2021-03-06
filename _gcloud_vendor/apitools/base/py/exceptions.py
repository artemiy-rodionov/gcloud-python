#!/usr/bin/env python
"""Exceptions for generated client libraries."""


class Error(Exception):
  """Base class for all exceptions."""


class TypecheckError(Error, TypeError):
  """An object of an incorrect type is provided."""


class NotFoundError(Error):
  """A specified resource could not be found."""


class UserError(Error):
  """Base class for errors related to user input."""


class InvalidDataError(Error):
  """Base class for any invalid data error."""


class CommunicationError(Error):
  """Any communication error talking to an API server."""


class HttpError(CommunicationError):
  """Error making a request. Soon to be HttpError."""

  def __init__(self, response, content, url):
    super(HttpError, self).__init__()
    self.response = response
    self.content = content
    self.url = url

  def __str__(self):
    content = self.content.decode('ascii', 'replace')
    return 'HttpError accessing <%s>: response: <%s>, content <%s>' % (
        self.url, self.response, content)

  @property
  def status_code(self):
    # TODO(craigcitro): Turn this into something better than a
    # KeyError if there is no status.
    return int(self.response['status'])

  @classmethod
  def FromResponse(cls, http_response):
    return cls(http_response.info, http_response.content,
               http_response.request_url)


class InvalidUserInputError(InvalidDataError):
  """User-provided input is invalid."""


class InvalidDataFromServerError(InvalidDataError, CommunicationError):
  """Data received from the server is malformed."""


class BatchError(Error):
  """Error generated while constructing a batch request."""


class ConfigurationError(Error):
  """Base class for configuration errors."""


class GeneratedClientError(Error):
  """The generated client configuration is invalid."""


class ConfigurationValueError(UserError):
  """Some part of the user-specified client configuration is invalid."""


class ResourceUnavailableError(Error):
  """User requested an unavailable resource."""


class CredentialsError(Error):
  """Errors related to invalid credentials."""


class TransferError(CommunicationError):
  """Errors related to transfers."""


class TransferInvalidError(TransferError):
  """The given transfer is invalid."""


class NotYetImplementedError(GeneratedClientError):
  """This functionality is not yet implemented."""


class StreamExhausted(Error):
  """Attempted to read more bytes from a stream than were available."""
