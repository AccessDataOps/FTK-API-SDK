## /api/users.py

"""
User classes to hold onto user information and updates values upon request.
 Integrates into the Client class to provide seamless use of the Exterro FTK API.
"""

from ..utilities import AttributeMappedDict

## Declaring __all__

__all__ = ("User", )

## User class construction

class User(AttributeMappedDict):
	"""User subclasses dict to maintain information about the
	relevant user within the platform.
	"""

	def __repr__(self):
		"""Return a string representation of the job.

		:rtype: string
		"""
		return f"User<id={self.id}, name={str(self.userName)}>"